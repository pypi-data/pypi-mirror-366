/*
* Code Contributors
* Mingyuan Wang
*/


#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include <iostream>
#include <math.h>
#include <stdlib.h>
#include <vector>
#include "scsutil.h"
#include <cmath>
#include "MovingAverageBased.h"
#include "QuantileBased.h"
#include <chrono>
#include <unordered_map>
#include <time.h>

using namespace std::chrono;
//****************************
using namespace std;


// Main Python function
static PyObject* OnlineDriftScreening(PyObject* self, PyObject* args) {
    // Parse input arguments
    int issparse;
    double alpha, beta, batchalpha;
    int bafreq, numb, factor, freq;
    PyObject* x_obj = NULL, * y_obj = NULL;
    char* path = NULL, * prefix = NULL, * extension = NULL;
    int totalfiles = 0, minibatch = 0;
	/*printf("initial\n");
	fflush(stdout);*/

	// Create a temporary tuple with just the first argument
	PyObject* temp_tuple = PyTuple_New(1);
	PyTuple_SetItem(temp_tuple, 0, PyTuple_GetItem(args, 0));

	// Now parse just the first argument
	if (!PyArg_ParseTuple(temp_tuple, "i", &issparse)) {
		Py_DECREF(temp_tuple);
		PyErr_SetString(PyExc_TypeError, "First argument must be integer");
		return NULL;
	}
	Py_DECREF(temp_tuple);

	/*printf("first arg get\n");
	fflush(stdout);*/
    // Get arguments based on whether input is sparse
    double* x = NULL, * y = NULL;
    int N = 0, P = 0;
	
	if (issparse) {
        if (!PyArg_ParseTuple(args, "idddiiiisssi",
            &issparse, &alpha, &beta, &batchalpha, &bafreq,
            &numb, &factor, &freq, &path, &prefix, &extension,
            &totalfiles)) {
            PyErr_SetString(PyExc_TypeError, "Invalid arguments");
            return NULL;
        }
		/*printf("all args parsed\n");
		fflush(stdout);*/
    }
    else {
        if (!PyArg_ParseTuple(args, "idddiiiiOOi",
            &issparse, &alpha, &beta, &batchalpha, &bafreq,
            &numb, &factor, &freq, &x_obj, &y_obj, &minibatch)) {
            PyErr_SetString(PyExc_TypeError, "Invalid arguments");
            return NULL;
        }
		/*printf("all args parsed\n");
		fflush(stdout);*/
		/*if (!PyArray_Check(x_obj)) {
			PyErr_SetString(PyExc_TypeError, "Input must be a NumPy array");
			return NULL;
		}*/
		/*printf("x_array start initial\n");
		fflush(stdout);*/
		PyArrayObject* x_array = (PyArrayObject*)x_obj;

		/*printf("x_array initialed\n");
		fflush(stdout);*/
		PyArrayObject* y_array = (PyArrayObject*)y_obj;
		/*printf("y initial\n");
		fflush(stdout);*/


        if (x_array == NULL || y_array == NULL) {
            Py_XDECREF(x_array);
            Py_XDECREF(y_array);
            PyErr_SetString(PyExc_TypeError, "x and y must be arrays");
            return NULL;
        }

		/*printf("xy start assign\n");
		fflush(stdout); */
        x = (double*)PyArray_DATA(x_array); //(PyArrayObject*)
        y = (double*)PyArray_DATA(y_array);
        N = (int)PyArray_DIM(x_array, 0); //(PyArrayObject*)
        P = (int)PyArray_DIM(x_array, 1);
		/*printf("x [%d, %d]\n", N, P);
		fflush(stdout);
		printf("y [%d, %d]\n", (int)PyArray_DIM(y_array, 0), (int)PyArray_DIM(y_array, 1));
		fflush(stdout);*/

		/*for (int i = 0; i < 5; i++) {
			printf("%f\n", x[i]);
			fflush(stdout);
		}*/
		/*printf("xy finish assign\n");
		fflush(stdout);*/

	}
	
    //simulate batch input
    int batchs = (int)ceil(N / (double)minibatch), numout;
    if (freq == 0) {
        numout = 1;
    }
    else {
        numout = (int)ceil(N / (double)freq);
    }
    int batchstart, batchend, batchSize, fnum = 1;
    double du1, du2;

	/*printf("simulation batch calculated\n");
	fflush(stdout);*/
    // Create output numpy arrays
    npy_intp dims[2];
    //PyObject* result = PyTuple_New(6); // Similar to MATLAB's 6 outputs

	if (numb > 0) {
		if (issparse) {
			if ((alpha < 1 && alpha >0) || (batchalpha < 1 && batchalpha >0)) {
				PySys_WriteStdout("train: has bin, is sparse, has alpha\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				
				//int varsize;
				OnlineQuantileNPunknownDrift<float, double, int, char> myOQ = OnlineQuantileNPunknownDrift<float, double, int, char>(factor, numb);
				/*Py_BEGIN_ALLOW_THREADS
				{*/
				//std::vector<int> varout;
				myOQ.InitFiles(path, prefix, extension, totalfiles, alpha, beta);
				int varsize = myOQ.TrainSummary(batchalpha);
				//varsize = myOQ.TrainSummary(batchalpha);
				/*}
				Py_END_ALLOW_THREADS*/
				/*printf("train: has bin, is sparse, has alpha\n");
				fflush(stdout);*/
				
				// Create output arrays
				dims[0] = numb * 2; dims[1] = varsize;
				PyObject* pBinCount = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				dims[0] = 1; dims[1] = varsize;
				PyObject* miscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				PyObject* chi2score = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				PyObject* giniscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				PyObject* varidx = PyArray_SimpleNew(1, &dims[1], NPY_INT32);

				/*double* pBinCount_data = (double*)PyArray_DATA((PyArrayObject*)pBinCount);
				double* miscore_data = (double*)PyArray_DATA((PyArrayObject*)miscore);
				double* chi2score_data = (double*)PyArray_DATA((PyArrayObject*)chi2score);
				double* giniscore_data = (double*)PyArray_DATA((PyArrayObject*)giniscore);
				int* varidx_data = (int*)PyArray_DATA((PyArrayObject*)varidx);*/
				/*PySys_WriteStdout("\toutside Finalizing\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");*/

				

				myOQ.Finalize((double*)PyArray_DATA((PyArrayObject*)pBinCount),
					(double*)PyArray_DATA((PyArrayObject*)miscore),
					(double*)PyArray_DATA((PyArrayObject*)chi2score),
					(double*)PyArray_DATA((PyArrayObject*)giniscore),
					(int*)PyArray_DATA((PyArrayObject*)varidx),
					du1, du2, batchalpha);
				/*Py_BEGIN_ALLOW_THREADS
				{
				myOQ.Finalize(pBinCount_data, miscore_data,	chi2score_data, giniscore_data,	varidx_data, du1, du2, batchalpha);
				}
				Py_END_ALLOW_THREADS*/
				/*PySys_WriteStdout("\toutside finalize\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");*/
				
				PyObject* result = PyTuple_New(7);
				PyTuple_SetItem(result, 0, pBinCount);
				PyTuple_SetItem(result, 1, miscore);
				PyTuple_SetItem(result, 2, chi2score);
				PyTuple_SetItem(result, 3, giniscore);
				PyTuple_SetItem(result, 4, PyFloat_FromDouble(du1));
				PyTuple_SetItem(result, 5, PyFloat_FromDouble(du2));
				PyTuple_SetItem(result, 6, varidx);
				PySys_WriteStdout("finish all\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				return result;
				/*PySys_WriteStdout("\tcomplete filling vars\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");*/
				
			}
			else {
				PySys_WriteStdout("train: has bin, is sparse, no alpha\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				OnlineQuantileNPunknown<float, double, int, char> myOQ = OnlineQuantileNPunknown<float, double, int, char>(factor, numb);
				std::set<int> varout;
				myOQ.InitFiles(path, prefix, extension, totalfiles);
				int varsize = myOQ.TrainSummary();
				/*printf("train: has bin, is sparse, no alpha\n");
				fflush(stdout);*/
				
				// Create output arrays
				dims[0] = numb * 2; dims[1] = varsize;
				PyObject* pBinCount = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				dims[0] = 1; dims[1] = varsize;
				PyObject* miscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				PyObject* chi2score = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				PyObject* giniscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				

				myOQ.Finalize((double*)PyArray_DATA((PyArrayObject*)pBinCount),
					(double*)PyArray_DATA((PyArrayObject*)miscore),
					(double*)PyArray_DATA((PyArrayObject*)chi2score),
					(double*)PyArray_DATA((PyArrayObject*)giniscore), varout, du1, du2);
				PyObject* varidx = PyArray_SimpleNew(1, &dims[1], NPY_INT32);
				int* varidx_data = (int*)PyArray_DATA((PyArrayObject*)varidx);
				/*plhs[6] = mxCreateNumericMatrix(1, varsize, mxINT32_CLASS, mxREAL);
				int* varidx = (int*)mxGetPr(plhs[6]);*/
				int thisi = 0;
				for (std::set<int>::iterator si = varout.begin(); si != varout.end(); ++si) {
					varidx_data[thisi] = *si;
					thisi++;
				}
				
				PyObject* result = PyTuple_New(7);
				PyTuple_SetItem(result, 0, pBinCount);
				PyTuple_SetItem(result, 1, miscore);
				PyTuple_SetItem(result, 2, chi2score);
				PyTuple_SetItem(result, 3, giniscore);
				PyTuple_SetItem(result, 4, PyFloat_FromDouble(du1));
				PyTuple_SetItem(result, 5, PyFloat_FromDouble(du2));
				PyTuple_SetItem(result, 6, varidx);
				PySys_WriteStdout("finish all\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				return result;
			}
		}
		else {
			if ((alpha < 1 && alpha >0) || (batchalpha < 1 && batchalpha >0)) {
				/*printf("train: has bin, no sparse, has alpha\n");
				fflush(stdout);*/
				PySys_WriteStdout("train: has bin, no sparse, has alpha\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");

				dims[0] = numb * 2; dims[1] = P;
				PyObject* pBinCount = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* pBinCount_data = (double*)PyArray_DATA((PyArrayObject*)pBinCount);
				dims[0] = numout; dims[1] = P;
				PyObject* miscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* miscore_data = (double*)PyArray_DATA((PyArrayObject*)miscore);
				PyObject* chi2score = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* chi2score_data = (double*)PyArray_DATA((PyArrayObject*)chi2score);
				PyObject* giniscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* giniscore_data = (double*)PyArray_DATA((PyArrayObject*)giniscore);
				OnlineQuantileNPknownDrift<float, double, int> myOQ = OnlineQuantileNPknownDrift<float, double, int>(factor, numb, P);
				//****non-sparce batch feeds******
				for (int b = 0; b < batchs; b++)
				{
					PySys_WriteStdout("batch %d\n", b);
					PyRun_SimpleString("import sys; sys.stdout.flush()");
					batchstart = b * minibatch;
					if (b != batchs - 1) {
						batchSize = minibatch;
						batchend = batchstart + minibatch - 1;
					}
					else {
						batchSize = N - (minibatch * b);
						batchend = N - 1;
					}

					vector<double> xbatch(P * batchSize, 0), ybatch(batchSize, 0);
					for (int j = 0; j < P; j++) {
						for (int r = batchstart; r <= batchend; r++) {
							xbatch[batchSize * j + r - batchstart] = x[N * j + r];
						}
					}
					for (int r = batchstart; r <= batchend; r++) {
						////debug
						//if (r == 410) {
						//	int check = 1;
						//}
						ybatch[r - batchstart] = y[r];
					}

					myOQ.stuffBatch(xbatch, ybatch, batchSize, alpha, beta);
					if (remainder(b + 1, bafreq) == 0) {
						myOQ.TrainSummary(batchalpha);
					}
					else {
						myOQ.TrainSummary(1);
					}
					// freq is used to output scores every freq rows, total numout times
					if (batchend + 1 == freq * fnum) {
						/*if (fnum == 20) {
							int check = 1;
						}*/
						std::vector<double> msc, csc, gsc;
						myOQ.FinalizeInterv(msc, csc, gsc, du1, du2);
						for (int j = 0; j < P; ++j) {
							miscore_data[numout * j + fnum - 1] = msc[j];
							chi2score_data[numout * j + fnum - 1] = csc[j];
							giniscore_data[numout * j + fnum - 1] = gsc[j];
						}
						printf("out put %d\n", fnum);
						fflush(stdout);
						fnum++;
					}
				}
				if (numout == 1) {
					//std::vector<double> msc, csc, gsc;
					myOQ.Finalize(pBinCount_data, miscore_data, chi2score_data, giniscore_data, du1, du2);
					/*for (int j = 0; j < P; ++j) {
						miscore[j] = msc[j];
						chi2score[j] = csc[j];
						giniscore[j] = gsc[j];
					}*/
				}
				PyObject* result = PyTuple_New(6);
				PyTuple_SetItem(result, 0, pBinCount);
				PyTuple_SetItem(result, 1, miscore);
				PyTuple_SetItem(result, 2, chi2score);
				PyTuple_SetItem(result, 3, giniscore);
				PyTuple_SetItem(result, 4, PyFloat_FromDouble(du1));
				PyTuple_SetItem(result, 5, PyFloat_FromDouble(du2));
				/*printf("\ttime of t1: %f\n", du1);
				fflush(stdout);*/
				PySys_WriteStdout("finish all\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				return result;
			}
			else {
				/*printf("train: has bin, no sparse, no alpha\n");
				fflush(stdout);*/
				PySys_WriteStdout("train: has bin, no sparse, no alpha\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");

				dims[0] = numb * 2; dims[1] = P;
				PyObject* pBinCount = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* pBinCount_data = (double*)PyArray_DATA((PyArrayObject*)pBinCount);
				dims[0] = numout; dims[1] = P;
				PyObject* miscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* miscore_data = (double*)PyArray_DATA((PyArrayObject*)miscore);
				PyObject* chi2score = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* chi2score_data = (double*)PyArray_DATA((PyArrayObject*)chi2score);
				PyObject* giniscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* giniscore_data = (double*)PyArray_DATA((PyArrayObject*)giniscore);
				OnlineQuantileNPknown<float, double, int> myOQ = OnlineQuantileNPknown<float, double, int>(factor, numb, P);
				//****non-sparce batch feeds******
				for (int b = 0; b < batchs; b++)
				{
					PySys_WriteStdout("batch %d\n", b);
					PyRun_SimpleString("import sys; sys.stdout.flush()");
					batchstart = b * minibatch;
					if (b != batchs - 1) {
						batchSize = minibatch;
						batchend = batchstart + minibatch - 1;
					}
					else {
						batchSize = N - (minibatch * b);
						batchend = N - 1;
					}

					vector<double> xbatch(P * batchSize, 0), ybatch(batchSize, 0);
					for (int j = 0; j < P; j++) {
						for (int r = batchstart; r <= batchend; r++) {
							xbatch[batchSize * j + r - batchstart] = x[N * j + r];
						}
					}
					for (int r = batchstart; r <= batchend; r++) {
						ybatch[r - batchstart] = y[r];
					}

					/*myOQ.stuffBatch(xbatch, ybatch, batchSize);
					myOQ.TrainSummary();*/

					/*if (fnum == 20) {
						int check = 1;
					}*/
					myOQ.stuffBatch(xbatch, ybatch, batchSize);
					myOQ.TrainSummary();
					if (batchend + 1 == freq * fnum) {

						//std::vector<double> msc, csc, gsc;
						myOQ.FinalizeInterv(miscore_data, chi2score_data, giniscore_data, du1, du2, numout, fnum);
						//myOQ.FinalizeInterv(msc, csc, gsc, du1, du2);
						//for (int j = 0; j < P; ++j) {
						//	miscore[numout * j + fnum - 1] = msc[j];
						//	chi2score[numout * j + fnum - 1] = csc[j];
						//	giniscore[numout * j + fnum - 1] = gsc[j];
						//}
						printf("out put %d\n", fnum);
						fflush(stdout);
						fnum++;
					}
				}
				if (numout == 1) {
					//std::vector<double> msc, csc, gsc;
					myOQ.Finalize(pBinCount_data, miscore_data, chi2score_data, giniscore_data, du1, du2);
					/*for (int j = 0; j < P; ++j) {
						miscore[j] = msc[j];
						chi2score[j] = csc[j];
						giniscore[j] = gsc[j];
					}*/
				}
				PyObject* result = PyTuple_New(6);
				PyTuple_SetItem(result, 0, pBinCount);
				PyTuple_SetItem(result, 1, miscore);
				PyTuple_SetItem(result, 2, chi2score);
				PyTuple_SetItem(result, 3, giniscore);
				PyTuple_SetItem(result, 4, PyFloat_FromDouble(du1));
				PyTuple_SetItem(result, 5, PyFloat_FromDouble(du2));
				/*printf("\ttime of t1: %f\n", du1);
				fflush(stdout);*/
				PySys_WriteStdout("finish all\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				return result;
				
			}
		}
	}
	else {
		if (issparse) {
			if ((alpha < 1 && alpha >0) || (batchalpha < 1 && batchalpha >0)) {
				/*printf("train: no bin, is sparse, has alpha\n");
				fflush(stdout);*/
				PySys_WriteStdout("train: no bin, is sparse, has alpha\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");

				MoveAVGDriftUnfixP<float, double, int, char> myOQ = MoveAVGDriftUnfixP<float, double, int, char>();
				std::set<int> varout;
				myOQ.InitFiles(path, prefix, extension, totalfiles, alpha, beta);
				int varsize = myOQ.TrainSummary(batchalpha);
				dims[0] = numout; dims[1] = varsize;
				PyObject* fishscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* fishscore_data = (double*)PyArray_DATA((PyArrayObject*)fishscore);
				PyObject* tscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* tscore_data = (double*)PyArray_DATA((PyArrayObject*)tscore);

				/*plhs[0] = mxCreateDoubleMatrix(numout, varsize, mxREAL);
				double* fishscore = (double*)mxGetPr(plhs[0]);*/
				/*plhs[1] = mxCreateDoubleMatrix(numout, varsize, mxREAL);
				double* tscore = (double*)mxGetPr(plhs[1]);*/
				myOQ.Finalize(fishscore_data, tscore_data, varout, du1, du2, batchalpha);
				PyObject* varidx = PyArray_SimpleNew(1, &dims[1], NPY_INT32);
				int* varidx_data = (int*)PyArray_DATA((PyArrayObject*)varidx);

				/*plhs[4] = mxCreateNumericMatrix(1, varsize, mxINT32_CLASS, mxREAL);
				int* varidx = (int*)mxGetPr(plhs[4]);*/
				int thisi = 0;
				for (std::set<int>::iterator si = varout.begin(); si != varout.end(); ++si) {
					varidx_data[thisi] = *si;
					thisi++;
				}
				//myOQ.Finalize(fishscore, tscore, du1, du2);
				/*printf("\ttime of t1: %f\n", du1);
				fflush(stdout);*/
				PyObject* result = PyTuple_New(5);
				PyTuple_SetItem(result, 0, fishscore);
				PyTuple_SetItem(result, 1, tscore);
				PyTuple_SetItem(result, 2, PyFloat_FromDouble(du1));
				PyTuple_SetItem(result, 3, PyFloat_FromDouble(du2));
				PyTuple_SetItem(result, 4, varidx);
				PySys_WriteStdout("finish all\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				return result;
			}
			else {
				/*printf("train: no bin, is sparse, no alpha\n");
				fflush(stdout);*/
				PySys_WriteStdout("train: no bin, is sparse, no alpha\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");

				MoveAVGUnfixP<float, double, int, char> myOQ = MoveAVGUnfixP<float, double, int, char>();
				std::set<int> varout;
				myOQ.InitFiles(path, prefix, extension, totalfiles);
				int varsize = myOQ.TrainSummary();
				dims[0] = numout; dims[1] = varsize;
				PyObject* fishscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* fishscore_data = (double*)PyArray_DATA((PyArrayObject*)fishscore);
				PyObject* tscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* tscore_data = (double*)PyArray_DATA((PyArrayObject*)tscore);

				/*plhs[0] = mxCreateDoubleMatrix(numout, varsize, mxREAL);
				double* fishscore = (double*)mxGetPr(plhs[0]);*/
				/*plhs[1] = mxCreateDoubleMatrix(numout, varsize, mxREAL);
				double* tscore = (double*)mxGetPr(plhs[1]);*/
				myOQ.Finalize(fishscore_data, tscore_data, varout, du1, du2);
				PyObject* varidx = PyArray_SimpleNew(1, &dims[1], NPY_INT32);
				int* varidx_data = (int*)PyArray_DATA((PyArrayObject*)varidx);

				/*plhs[4] = mxCreateNumericMatrix(1, varsize, mxINT32_CLASS, mxREAL);
				int* varidx = (int*)mxGetPr(plhs[4]);*/
				int thisi = 0;
				for (std::set<int>::iterator si = varout.begin(); si != varout.end(); ++si) {
					varidx_data[thisi] = *si;
					thisi++;
				}
				//myOQ.Finalize(fishscore, tscore, du1, du2);
				/*printf("\ttime of t1: %f\n", du1);
				fflush(stdout);*/
				PyObject* result = PyTuple_New(5);
				PyTuple_SetItem(result, 0, fishscore);
				PyTuple_SetItem(result, 1, tscore);
				PyTuple_SetItem(result, 2, PyFloat_FromDouble(du1));
				PyTuple_SetItem(result, 3, PyFloat_FromDouble(du2));
				PyTuple_SetItem(result, 4, varidx);
				PySys_WriteStdout("finish all\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				return result;
			}
		}
		else {
			if ((alpha < 1 && alpha >0) || (batchalpha < 1 && batchalpha >0)) {
				/*printf("train: no bin, no sparse, has alpha\n");
				fflush(stdout);*/
				PySys_WriteStdout("train: no bin, no sparse, has alpha\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");

				dims[0] = numout; dims[1] = P;
				/*printf("scores dim assigned %d, %d\n", dims[0], dims[1]);
				fflush(stdout);*/
				PyObject* fishscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				/*printf("instantaniase score\n");
				fflush(stdout);*/
				double* fishscore_data = (double*)PyArray_DATA((PyArrayObject*)fishscore);
				/*printf("set pointer\n");
				fflush(stdout);*/
				PyObject* tscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* tscore_data = (double*)PyArray_DATA((PyArrayObject*)tscore);
				/*printf("initiated scores\n");
				fflush(stdout);*/
				/*plhs[0] = mxCreateDoubleMatrix(numout, P, mxREAL);
				double* fishscore = (double*)mxGetPr(plhs[0]);
				plhs[1] = mxCreateDoubleMatrix(numout, P, mxREAL);
				double* tscore = (double*)mxGetPr(plhs[1]);*/
				MoveAVGDriftFixP<float, double, int> myOQ = MoveAVGDriftFixP<float, double, int>(P);
				/*printf("initiated calculation\n");
				fflush(stdout);*/
				//****non-sparce batch feeds******
				for (int b = 0; b < batchs; b++)
				{
					PySys_WriteStdout("batch %d\n", b);
					PyRun_SimpleString("import sys; sys.stdout.flush()");
					batchstart = b * minibatch;
					if (b != batchs - 1) {
						batchSize = minibatch;
						batchend = batchstart + minibatch - 1;
					}
					else {
						batchSize = N - (minibatch * b);
						batchend = N - 1;
					}

					vector<double> xbatch(P * batchSize, 0), ybatch(batchSize, 0);
					for (int j = 0; j < P; j++) {
						for (int r = batchstart; r <= batchend; r++) {
							xbatch[batchSize * j + r - batchstart] = x[N * j + r];
						}
					}
					for (int r = batchstart; r <= batchend; r++) {
						////debug
						//if (r == 410) {
						//	int check = 1;
						//}
						ybatch[r - batchstart] = y[r];
					}
					//debug
					/*if (b == 49) {
						int check = 1;
					}*/
					/*printf("get batch\n");
					fflush(stdout);*/
					myOQ.stuffData(xbatch, ybatch, alpha, beta, batchSize);
					/*printf("updated\n");
					fflush(stdout);*/
					if (remainder(b + 1, bafreq) == 0) {
						myOQ.TrainSummary(batchalpha);
					}
					else {
						myOQ.TrainSummary(1);
					}
					if (numout != 1) {
						if (batchend + 1 == freq * fnum) {
							std::vector<double> fsc, tsc;
							myOQ.Finalize(fsc, tsc, du1, du2);
							for (int j = 0; j < P; ++j) {
								fishscore_data[numout * j + fnum - 1] = fsc[j];
								tscore_data[numout * j + fnum - 1] = tsc[j];
							}
							printf("output %d\n", fnum);
							fflush(stdout);
							fnum++;
						}
					}
				}
				/*printf("finish loop\n");
				fflush(stdout);*/
				npy_intp* checkdims = PyArray_DIMS((PyArrayObject*)fishscore);
				/*printf("fishscore dim assigned %" NPY_INTP_FMT ", %" NPY_INTP_FMT "\n", checkdims[0], checkdims[1]);
				fflush(stdout);*/
				if (numout == 1) {
					std::vector<double> fsc, tsc;
					myOQ.Finalize(fsc, tsc, du1, du2);
					/*printf("fsc size %zu\n", fsc.size());
					fflush(stdout);*/
					for (int j = 0; j < P; ++j) {
						fishscore_data[j] = fsc[j];
						/*printf("imp %f\n", fsc[j]);
						fflush(stdout);*/
						tscore_data[j] = tsc[j];
					}
				}
				//myOQ.Finalize(fishscore, tscore, du1, du2);
				/*printf("\ttime of t1: %f\n", du1);
				fflush(stdout);*/
				PyObject* result = PyTuple_New(4);
				PyTuple_SetItem(result, 0, fishscore);
				PyTuple_SetItem(result, 1, tscore);
				PyTuple_SetItem(result, 2, PyFloat_FromDouble(du1));
				PyTuple_SetItem(result, 3, PyFloat_FromDouble(du2));
				/*PyObject* result = PyTuple_New(2);
				PyTuple_SetItem(result, 0, PyFloat_FromDouble(du1));
				PyTuple_SetItem(result, 1, PyFloat_FromDouble(du2));*/
				PySys_WriteStdout("finish all\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				return result;
				/*plhs[2] = mxCreateDoubleScalar(du1);
				plhs[3] = mxCreateDoubleScalar(du2);*/
			}
			else {
				/*printf("train: no bin, no sparse, no alpha\n");
				fflush(stdout);*/
				PySys_WriteStdout("train: no bin, no sparse, no alpha\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");

				dims[0] = numout; dims[1] = P;
				PyObject* fishscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* fishscore_data = (double*)PyArray_DATA((PyArrayObject*)fishscore);
				PyObject* tscore = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
				double* tscore_data = (double*)PyArray_DATA((PyArrayObject*)tscore);
				
				/*plhs[0] = mxCreateDoubleMatrix(numout, P, mxREAL);
				double* fishscore = (double*)mxGetPr(plhs[0]);
				plhs[1] = mxCreateDoubleMatrix(numout, P, mxREAL);
				double* tscore = (double*)mxGetPr(plhs[1]);*/
				MoveAVGFixP<float, double, int> myOQ = MoveAVGFixP<float, double, int>(P);
				//****non-sparce batch feeds******
				for (int b = 0; b < batchs; b++)
				{
					PySys_WriteStdout("batch %d\n", b);
					PyRun_SimpleString("import sys; sys.stdout.flush()");
					batchstart = b * minibatch;
					if (b != batchs - 1) {
						batchSize = minibatch;
						batchend = batchstart + minibatch - 1;
					}
					else {
						batchSize = N - (minibatch * b);
						batchend = N - 1;
					}

					vector<double> xbatch(P * batchSize, 0), ybatch(batchSize, 0);
					for (int j = 0; j < P; j++) {
						for (int r = batchstart; r <= batchend; r++) {
							xbatch[batchSize * j + r - batchstart] = x[N * j + r];
						}
					}
					for (int r = batchstart; r <= batchend; r++) {
						ybatch[r - batchstart] = y[r];
					}

					myOQ.stuffData(xbatch, ybatch, batchSize);
					myOQ.TrainSummary();
					if (numout != 1) {
						if (batchend + 1 == freq * fnum) {
							std::vector<double> fsc, tsc;
							myOQ.Finalize(fsc, tsc, du1, du2);
							for (int j = 0; j < P; ++j) {
								fishscore_data[numout * j + fnum - 1] = fsc[j];
								tscore_data[numout * j + fnum - 1] = tsc[j];
							}
							printf("output %d\n", fnum);
							fflush(stdout);
							fnum++;
						}
					}
				}
				if (numout == 1) {
					std::vector<double> fsc, tsc;
					myOQ.Finalize(fsc, tsc, du1, du2);
					for (int j = 0; j < P; ++j) {
						fishscore_data[j] = fsc[j];
						tscore_data[j] = tsc[j];
					}
				}
				//myOQ.Finalize(fishscore, tscore, du1, du2);
				/*printf("\ttime of t1: %f\n", du1);
				fflush(stdout);*/
				PyObject* result = PyTuple_New(4);
				PyTuple_SetItem(result, 0, fishscore);
				PyTuple_SetItem(result, 1, tscore);
				PyTuple_SetItem(result, 2, PyFloat_FromDouble(du1));
				PyTuple_SetItem(result, 3, PyFloat_FromDouble(du2));
				PySys_WriteStdout("finish all\n");
				PyRun_SimpleString("import sys; sys.stdout.flush()");
				return result;
			}
		}
	}
	/*PySys_WriteStdout("finish all\n");
	PyRun_SimpleString("import sys; sys.stdout.flush()");
	return result;*/
}

// Method table
static PyMethodDef FsonlineMethods[] = {
	{"OnlineDriftScreening", OnlineDriftScreening, METH_VARARGS, "All in one online screening function for regualr, sparse, and drifting data stream"},
	{NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef module_def = {
	PyModuleDef_HEAD_INIT,
	"fsonline", "Module docstring", -1, FsonlineMethods
};

// Entry point
PyMODINIT_FUNC PyInit_fsonline(void) {
	import_array();
	PyObject* module = PyModule_Create(&module_def);  
	return module;
}


