// Copyright (c) 2008, Casey Duncan (casey dot duncan at gmail dot com)
// Copyright (c) 2022, Max Shinn
// see LICENSE.txt for details

#include "Python.h"
#include <math.h>
#include <stdio.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

#ifdef _MSC_VER
#define inline __inline
#endif

#define lerp(t, a, b) ((a) + (t) * ((b) - (a)))

const float GRAD3[][3] = {
	{1,1,0},{-1,1,0},{1,-1,0},{-1,-1,0}, 
	{1,0,1},{-1,0,1},{1,0,-1},{-1,0,-1}, 
	{0,1,1},{0,-1,1},{0,1,-1},{0,-1,-1},
	{1,0,-1},{-1,0,-1},{0,-1,1},{0,1,1}};


#define PERM_SIZE 4096
#define PERM_MASK (PERM_SIZE-1)
static unsigned short PERM[PERM_SIZE * 2];

static void init_perm(unsigned int seed)
{
    for (unsigned int i = 0; i < PERM_SIZE; ++i) PERM[i] = i;
    // Fisher-Yates shuffle
    srand(seed);
    for (unsigned int i = PERM_SIZE-1; i; --i) {
        unsigned int j = rand() & PERM_MASK;
        unsigned short t = PERM[i];
        PERM[i] = PERM[j];
        PERM[j] = t;
    }
    // duplicate so PERM[i + PERM_SIZE] is always valid
    for (unsigned int i = 0; i < PERM_SIZE; ++i)
        PERM[PERM_SIZE + i] = PERM[i];
}



static inline float
grad3(const int hash, const float x, const float y, const float z)
{
	const int h = hash & 15;
	return x * GRAD3[h][0] + y * GRAD3[h][1] + z * GRAD3[h][2];
}

float
noise3(float x, float y, float z, const int repeatx, const int repeaty, const int repeatz, 
	const int base)
{
	float fx, fy, fz;
	int A, AA, AB, B, BA, BB;
	int i = (int)x;
  int j = (int)y;
  int k = (int)z;
	int ii = (i + 1) %  repeatx;
	int jj = (j + 1) % repeaty;
	int kk = (k + 1) % repeatz;
	i = ((i + base) & PERM_MASK);
	j = ((j + base) & PERM_MASK);
	k = ((k + base) & PERM_MASK);
	ii = ((ii + base) & PERM_MASK);
	jj = ((jj + base) & PERM_MASK);
	kk = ((kk + base) & PERM_MASK);

	x -= (float)(int)x; y -= (float)(int)y; z -= (float)(int)z;
	fx = x*x*x * (x * (x * 6 - 15) + 10);
	fy = y*y*y * (y * (y * 6 - 15) + 10);
	fz = z*z*z * (z * (z * 6 - 15) + 10);

	A = PERM[i];
	AA = PERM[(A + j) & PERM_MASK];
	AB = PERM[(A + jj) & PERM_MASK];
	B = PERM[ii];
	BA = PERM[(B + j) & PERM_MASK];
	BB = PERM[(B + jj) & PERM_MASK];

	return lerp(fz, lerp(fy, lerp(fx, grad3(PERM[AA + k], x, y, z),
									  grad3(PERM[BA + k], x - 1, y, z)),
							 lerp(fx, grad3(PERM[AB + k], x, y - 1, z),
									  grad3(PERM[BB + k], x - 1, y - 1, z))),
					lerp(fy, lerp(fx, grad3(PERM[AA + kk], x, y, z - 1),
									  grad3(PERM[BA + kk], x - 1, y, z - 1)),
							 lerp(fx, grad3(PERM[AB + kk], x, y - 1, z - 1),
									  grad3(PERM[BB + kk], x - 1, y - 1, z - 1))));
}

static PyObject *
make_perlin(PyObject *self, PyObject *args, PyObject *kwargs)
{
	int octaves = 1;
	float persistence = 0.5f;
  float lacunarity = 2.0f;
	int repeatx = 1024; // arbitrary
	int repeaty = 1024; // arbitrary
	int repeatz = 1024; // arbitrary
	int base = 0;


  float *x, *y, *z;
  PyArrayObject *_x, *_y, *_z;
  PyObject *__x, *__y, *__z;

	static char *kwlist[] = {"x", "y", "z", "octaves", "persistence", "lacunarity",
		"repeatx", "repeaty", "repeatz", "base", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOO|iffiiii:noise3", kwlist,
		&__x, &__y, &__z, &octaves, &persistence, &lacunarity, &repeatx, &repeaty, &repeatz, &base))
		return NULL;
  if (base < 0 || base >= PERM_SIZE) {
    PyErr_SetString(PyExc_ValueError, "Base must be between 0 and 4096");
    return NULL;
  }
  _x = (PyArrayObject*)PyArray_FROMANY(__x, NPY_FLOAT, 1, 1, NPY_ARRAY_C_CONTIGUOUS);
  _y = (PyArrayObject*)PyArray_FROMANY(__y, NPY_FLOAT, 1, 1, NPY_ARRAY_C_CONTIGUOUS);
  _z = (PyArrayObject*)PyArray_FROMANY(__z, NPY_FLOAT, 1, 1, NPY_ARRAY_C_CONTIGUOUS);
  if (!_x || !_y || !_z)
    return NULL;
  x = (float*)PyArray_DATA(_x);
  y = (float*)PyArray_DATA(_y);
  z = (float*)PyArray_DATA(_z);
  int len_x = PyArray_SIZE(_x);
  int len_y = PyArray_SIZE(_y);
  int len_z = PyArray_SIZE(_z);
  int i,j,k,l;
  float *ret = (float*)malloc(sizeof(float)*len_x*len_y*len_z);
  if (x[len_x-1] >= repeatx || y[len_y-1] >= repeaty || z[len_z-1] >= repeatz) {
		PyErr_SetString(PyExc_ValueError, "Cannot pass values greater than repeatx/y/z");
    return NULL;
  }

	if (octaves == 1) {
		// Single octave, return simple noise
    for (i=0; i<len_x; i++) {
      for (j=0; j<len_y; j++) {
        for (k=0; k<len_z; k++) {
          ret[i*len_y*len_z+j*len_z+k] = noise3(x[i], y[j], z[k],
                                                repeatx, repeaty, repeatz, base);
        }
      }
    }
	} else if (octaves > 1) {
    for (i=0; i<len_x; i++) {
      for (j=0; j<len_y; j++) {
        for (k=0; k<len_z; k++) {
          float freq = 1.0f;
          float amp = 1.0f;
          float max = 0.0f;
          float total = 0.0f;
          for (l = 0; l < octaves; l++) {
            total += noise3(x[i] * freq, y[j] * freq, z[k] * freq,
              (const int)(repeatx*freq), (const int)(repeaty*freq), (const int)(repeatz*freq), base) * amp;
            max += amp;
            freq *= lacunarity;
            amp *= persistence;
            if (amp < .004) break; // No chance of influence beyond ~1/256
          }
          ret[i*len_y*len_z+j*len_z+k] = (float) (total / max);
        }
      }
    }
	} else {
		PyErr_SetString(PyExc_ValueError, "Expected octaves value > 0");
		return NULL;
	}
  npy_intp dims[3] = { len_x, len_y, len_z };
  PyObject *retarray = PyArray_SimpleNewFromData(3, dims, NPY_FLOAT, ret);
  PyArray_ENABLEFLAGS((PyArrayObject*)retarray, NPY_ARRAY_OWNDATA);
  Py_DECREF(_x);
  Py_DECREF(_y);
  Py_DECREF(_z);
  return retarray;
}

static PyMethodDef perlin_functions[] = {
	{"make_perlin", (PyCFunction) make_perlin, METH_VARARGS | METH_KEYWORDS,
    "Generate a perlin noise stimulus\n\
\n\
    Parameters\n\
    ----------\n\
    x,y,z : 1D ndarray of float32, length > 0\n\
        Grid of positions on which to compute the noise\n\
    octaves : int > 0, default: 1\n\
        Number of spatial scales to include\n\
    persistence : float > 0, default: 0.5\n\
        Relative strength of neighbouring octaves\n\
    repeatx,repeaty,repeatz : int > 0, default: 1024\n\
        Maximum x, y, or z value before the stimulus repeats\n\
    base : int ∈ [0,255], default: 0\n\
        Start position of the permutation, essentially the random seed\n\
\n\
    Returns\n\
    -------\n\
    3D int ndarray, values ∈ [0,255]\n\
        Pink noise movie\n\
"},
	{NULL}
};

PyDoc_STRVAR(module_doc, "Efficiently generate Perlin noise, based on the 'noise' package by Casey Duncan");

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"_perlin",
	module_doc,
	-1,                 /* m_size */
	perlin_functions,   /* m_methods */
	NULL,               /* m_reload (unused) */
	NULL,               /* m_traverse */
	NULL,               /* m_clear */
	NULL                /* m_free */
};

PyObject *
PyInit__perlin(void)
{
  import_array();
  init_perm(0);
  return PyModule_Create(&moduledef);
}
