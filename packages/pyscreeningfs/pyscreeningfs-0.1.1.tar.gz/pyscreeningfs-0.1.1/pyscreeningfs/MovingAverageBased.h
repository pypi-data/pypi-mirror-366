/*
* Code Contributors
* Mingyuan Wang
*/
#ifndef MOVEAVG_H_
#define MOVEAVG_H_
#include <iostream>
#include <math.h>
#include <stdlib.h>
#include <set>
#include <vector>
#include <cmath>
#include <chrono> 
#include <unordered_map> 
#include <time.h>
#include <string.h>

using namespace std::chrono;
using namespace std;

template<typename DType>
class Entry {
public:
	/*! \brief the mean0 */
	DType m0;
	/*! \brief the mean squares0 */
	DType ms0;
	/*! \brief the mean1 */
	DType m1;
	/*! \brief the mean squares1 */
	DType ms1;


	Entry() {}  // NOLINT
					 // constructor
	Entry( DType m0, DType ms0,DType m1, DType ms1)
		: m0(m0), ms0(ms0), m1(m1), ms1(ms1) {}
};

template<typename DType>
class DriftEntry {
public:
	/*! \brief the mean0 */
	DType m0;
	/*! \brief the mean squares0 */
	DType ms0;
	/*! \brief the weighted label count0 */
	DType w0;
	/*! \brief the mean1 */
	DType m1;
	/*! \brief the mean squares1 */
	DType ms1;
	/*! \brief the weighted label count1 */
	DType w1;

	DriftEntry() {}  // NOLINT
					 // constructor
	DriftEntry(DType m0, DType ms0, DType w0, DType m1, DType ms1, DType w1)
		: m0(m0), ms0(ms0), w0(w0), m1(m1), ms1(ms1), w1(w1) {}
};

template<typename FType, typename DType, typename IType>
class MoveAVGFixP {
private:
	vector<double> _x, _y;
	IType  _P, _N;//_batchSize, batchnum,
	//int startsummary, stream_seg, stream_start, stream_end, initSize, backup_start, backup_end, backup_seg, backup_initsize, backup_startsumm, batchend;
	std::unordered_map<int, Entry<DType>> sketch_collections;
	//const int weight = 1;
	//high_resolution_clock::time_point startT, stopT;
	//std::chrono::duration<double, std::milli> binTime, scoreTime;
protected:
	//IType _factor, _numbin;
	double c1, c0;
	int weight = 1;
	high_resolution_clock::time_point startT, stopT;
	std::chrono::duration<double, std::milli> binTime, scoreTime;

public:
	MoveAVGFixP(IType P) {//IType factor, IType numbin,
	/*	_factor = factor;
		_numbin = numbin;*/
		_P = P;
		c1 = 0;
		c0 = 0;
	}
	MoveAVGFixP() {//IType factor, IType numbin,
	/*	_factor = factor;
		_numbin = numbin;*/
		c1 = 0;
		c0 = 0;
	}
	//virtual vector<double> &Get_x(){return _x;}

	void stuffData(vector<double>& x, vector<double>& y, IType N);// , IType batchSize);

	void TrainSummary();

	void Finalize(vector<double>& fishscore, vector<double>& tscore, DType& bTime, DType& sTime);
};

template<typename FType, typename DType, typename IType>
class MoveAVGDriftFixP:public MoveAVGFixP<FType, DType, IType> {
protected:
	vector<double> _x, _y;
	IType  _P, _N;//_batchSize, batchnum,
	double _beta, _alpha;
	//int startsummary, stream_seg, stream_start, stream_end, initSize, backup_start, backup_end, backup_seg, backup_initsize, backup_startsumm, batchend;
	std::unordered_map<int, DriftEntry<DType>> sketch_collections;
	//const int weight = 1;
	//high_resolution_clock::time_point startT, stopT;
	//std::chrono::duration<double, std::milli> binTime, scoreTime;

public:
	MoveAVGDriftFixP(IType P) : MoveAVGFixP(0){//IType factor, IType numbin,
	/*	_factor = factor;
		_numbin = numbin;*/
		_P = P;
		c1 = 0;
		c0 = 0;
	}

	//virtual vector<double> &Get_x(){return _x;}

	void stuffData(vector<double>& x, vector<double>& y, double alpha, double beta, IType N);// , IType batchSize);

	void TrainSummary(double batchalpha);

	void Finalize(vector<double>& fishscore, vector<double>& tscore, DType& bTime, DType& sTime);
};

template<typename FType, typename DType, typename IType, typename CType>
class MoveAVGUnfixP :public MoveAVGFixP<FType, DType, IType> {
protected:
	std::set<int> vars;
	char name[255], * _path, * _prefix, * _extension;
	int _totalfiles, nrows, d, penaltimes;//_batchSize, batchnum,
	//std::vector<double> generalweight, tower0, tower1;
	//int startsummary, stream_seg, stream_start, stream_end, initSize, backup_start, backup_end, backup_seg, backup_initsize, backup_startsumm, batchend;
	std::unordered_map<int, Entry<DType>> sketch_collections;
	//std::vector<int> Yid;
	high_resolution_clock::time_point debug1, debug2, debug4, debug5, debug7, debug8, debug10, debug11;
	std::chrono::duration<double, std::milli> debug3, debug6, debug9, debug12;
	//const int weight = 1;
	//high_resolution_clock::time_point startT, stopT;
	//std::chrono::duration<double, std::milli> binTime, scoreTime;

public:
	MoveAVGUnfixP() : MoveAVGFixP() {//IType factor, IType numbin,
		/*	_factor = factor;
			_numbin = numbin;*/
		c1 = 0;
		c0 = 0;
		/*generalweight.push_back(0.0);
		generalweight.push_back(0.0);*/
	}

	//virtual vector<double> &Get_x(){return _x;}

	void InitFiles(CType* path, CType* prefix, CType* extension, IType totalfiles);// , IType batchSize);

	int TrainSummary();

	void Finalize(double* fishscore, double* tscore, std::set<int>& varout, DType& bTime, DType& sTime);
};


template<typename FType, typename DType, typename IType, typename CType>
class MoveAVGDriftUnfixP :public MoveAVGFixP<FType, DType, IType> {
protected:
	std::set<int> vars;
	char name[255], * _path, * _prefix, * _extension;
	int _totalfiles, nrows, d, penaltimes;//_batchSize, batchnum,
	double _beta, _alpha;
	std::vector<double> generalweight, tower0, tower1;
	//int startsummary, stream_seg, stream_start, stream_end, initSize, backup_start, backup_end, backup_seg, backup_initsize, backup_startsumm, batchend;
	std::unordered_map<int, std::pair<std::vector<int>, DriftEntry<DType>>> sketch_collections;
	//std::vector<int> Yid;
	high_resolution_clock::time_point debug1, debug2, debug4, debug5, debug7, debug8, debug10, debug11;
	std::chrono::duration<double, std::milli> debug3, debug6, debug9, debug12;
	//const int weight = 1;
	//high_resolution_clock::time_point startT, stopT;
	//std::chrono::duration<double, std::milli> binTime, scoreTime;

public:
	MoveAVGDriftUnfixP() : MoveAVGFixP() {//IType factor, IType numbin,
	/*	_factor = factor;
		_numbin = numbin;*/
		c1 = 0;
		c0 = 0;
		generalweight.push_back(0.0);
		generalweight.push_back(0.0);
	}

	//virtual vector<double> &Get_x(){return _x;}

	void InitFiles(CType* path, CType* prefix, CType* extension, IType totalfiles, double alpha, double beta);// , IType batchSize);

	int TrainSummary(double batchalpha);

	void Finalize(double* fishscore, double* tscore, std::set<int>& varout, DType& bTime, DType& sTime, double batchalpha);
};

//=======================no sparse no drift=======================
template<typename FType, typename DType, typename IType>
void MoveAVGFixP<FType, DType, IType>::stuffData(vector<double>& x, vector<double>& y, IType N) {//IType batchSize
	//startT = high_resolution_clock::now();
	//batchend = batchSize;
	_N = N;
	_x = x;
	_y = y;
	//// ctime() used to give the present time 
	//stopT = high_resolution_clock::now();
	//printf("\ttime of stuffBatch: %f\n", (stopT - startT).count());
	//fflush(stdout);
}

template<typename FType, typename DType, typename IType>
void MoveAVGFixP<FType, DType, IType>::TrainSummary() {
	startT = high_resolution_clock::now();
	double tempc1, tempc0;
	for (int j = 0; j < _P; j++) {
		tempc1 = c1, tempc0 = c0;
		for (int i = 0; i < _N; i++) {
			int label = (int)_y[i];
			if (label == 1) {
				tempc1++;

				int col = j;
				int addre = _N * j + i;
				double v = _x[addre];//n*j+i
				std::unordered_map<int, Entry<DType>>::iterator fi = sketch_collections.find(col);
				if (fi == sketch_collections.end()) {
					Entry<DType> tempentry = Entry<DType>(0, 0, v, pow(v,2));
					sketch_collections.insert(std::unordered_map<int, Entry<DType>>::value_type(col, tempentry));
				}
				else {
					//if(tempc1>=2) 
					fi->second.ms1 = (tempc1 - 1) / tempc1 * (fi->second.ms1) + 1 / tempc1 * pow(v, 2);
					fi->second.m1 = (tempc1 - 1) / tempc1 * (fi->second.m1) + v / tempc1;
				}

			}
			else {
				tempc0++;

				int col = j;
				int addre = _N * j + i;
				double v = _x[addre];//n*j+i
				std::unordered_map<int, Entry<DType>>::iterator fi = sketch_collections.find(col);
				if (fi == sketch_collections.end()) {
					Entry<DType> tempentry = Entry<DType>(v, pow(v, 2), 0, 0);
					sketch_collections.insert(std::unordered_map<int, Entry<DType>>::value_type(col, tempentry));
				}
				else {
					//if (tempc0 >= 2) 
					fi->second.ms0 = (tempc0 - 1) / tempc0 * (fi->second.ms0) + 1 / tempc0 * pow(v, 2);
					fi->second.m0 = (tempc0 - 1) / tempc0 * (fi->second.m0) + v / tempc0;
				}

			}

		}//end of each feature
		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//// ctime() used to give the present time 
		//printf("\ttime of TrainSummary: %f\n", (stopT - startT).count());
		//fflush(stdout);
	}
	c1 = tempc1, c0 = tempc0;
}

template<typename FType, typename DType, typename IType>
void MoveAVGFixP<FType, DType, IType>::Finalize(vector<double>& fishscore, vector<double>& tscore, DType& bTime, DType& sTime) {
	double n = c1 + c0;
	int totalf = (int)sketch_collections.size();
	//using LabelEntry = LabelEntry<float, double, int>;
	for (int i = 0; i < totalf; ++i) {
		startT = high_resolution_clock::now();
		std::unordered_map<int, Entry<DType>>::iterator fi = sketch_collections.find(i);


		//********t score*************
		startT = high_resolution_clock::now();
		double m1, m0, v1, v0, m;
		m1 = fi->second.m1;
		m0 = fi->second.m0;
		v1 = fi->second.ms1 - pow(m1, 2);
		v0 = fi->second.ms0 - pow(m0, 2);
		if (v1 + v0 > 0)
			tscore.push_back(abs(m1-m0)/sqrt(v1/c1+v0/c0));
		else
			tscore.push_back(0);

		//********fisher*************
		m = (m1 * c1 + m0 * c0) / (c1 + c0);
		if (v1 == 0 && v0 == 0)
			fishscore.push_back(0);
		else
			fishscore.push_back((c1 * (m1 - m) * (m1 - m) + c0 * (m0 - m) * (m0 - m)) / (c1 * v1 + c0 * v0));

		stopT = high_resolution_clock::now();
		scoreTime += stopT - startT;
	}

	bTime = binTime.count();
	sTime = scoreTime.count();
	//// ctime() used to give the present time 
	//time_t my_time = time(NULL);
	//printf("\ttime of TrainSummary: %f\n", (stopT - startT).count());
	//fflush(stdout);
	//std::unordered_map<int, std::vector<NoneDriftQSketch>>().swap(sketch_collections);
}
//=================no sparse drift========================
template<typename FType, typename DType, typename IType>
void MoveAVGDriftFixP<FType, DType, IType>::stuffData(vector<double>& x, vector<double>& y, double alpha, double beta, IType N) {//IType batchSize
	//startT = high_resolution_clock::now();
	//batchend = batchSize;
	_beta = beta;
	_alpha = alpha;
	_N = N;
	_x = x;
	_y = y;
	//// ctime() used to give the present time 
	//stopT = high_resolution_clock::now();
	//printf("\ttime of stuffBatch: %f\n", (stopT - startT).count());
	//fflush(stdout);
}

template<typename FType, typename DType, typename IType>
void MoveAVGDriftFixP<FType, DType, IType>::TrainSummary(double batchalpha) {
	startT = high_resolution_clock::now();
	double tempc1, tempc0;
	for (int j = 0; j < _P; j++) {
		std::unordered_map<int, DriftEntry<DType>>::iterator fi = sketch_collections.find(j);
		if (fi != sketch_collections.end() && batchalpha) {
			fi->second.ms1 = batchalpha * (fi->second.ms1);
			fi->second.m1 = batchalpha * (fi->second.m1);
			fi->second.w1 = batchalpha * (fi->second.w1);
			fi->second.ms0 = batchalpha * (fi->second.ms0);
			fi->second.m0 = batchalpha * (fi->second.m0);
			fi->second.w0 = batchalpha * (fi->second.w0);
		}
		tempc1 = c1, tempc0 = c0;
		for (int i = 0; i < _N; i++) {
			int label = (int)_y[i];
			if (label == 1) {
				tempc1++;
				int col = j;
				int addre = _N * j + i;
				double v = _x[addre];//n*j+i				
				if (fi == sketch_collections.end()) {
					DriftEntry<DType> tempentry = DriftEntry<DType>(0, 0, 0, v, pow(v, 2), 1);
					sketch_collections.insert(std::unordered_map<int, DriftEntry<DType>>::value_type(col, tempentry));
					fi = sketch_collections.find(col);
				}
				else {
					double thisalpha, thisbeta;
					if (_alpha == 1 && _beta == 1) {
						thisalpha = 1 - 1 / tempc1;
						thisbeta = 1 / tempc1;
					}
					else {
						thisalpha = _alpha;
						thisbeta = _beta;
					}
					fi->second.ms1 = thisalpha * (fi->second.ms1) + thisbeta * pow(v, 2);
					//fi->second.v1 = (1 - _beta) * (fi->second.v1) + (1 - _beta) * _beta * pow(fi->second.m1 - v, 2);
					fi->second.m1 = thisalpha * (fi->second.m1) + v * thisbeta;
					fi->second.w1 = _alpha * (fi->second.w1) + _beta;
					fi->second.ms0 = _alpha * (fi->second.ms0);
					//fi->second.v0 = pow((1 - _beta), 2) * (fi->second.v0); //+ (1 - _beta) * _beta * pow(fi->second.m0, 2);
					fi->second.m0 = _alpha * (fi->second.m0);
					fi->second.w0 = _alpha * (fi->second.w0);
				}

			}
			else {
				tempc0++;
				int col = j;
				int addre = _N * j + i;
				double v = _x[addre];//n*j+i
				if (fi == sketch_collections.end()) {
					DriftEntry<DType> tempentry = DriftEntry<DType>(v, pow(v, 2), 1, 0, 0, 0);
					sketch_collections.insert(std::unordered_map<int, DriftEntry<DType>>::value_type(col, tempentry));
					fi = sketch_collections.find(col);
				}
				else {
					double thisalpha, thisbeta;
					if (_alpha == 1 && _beta == 1) {
						thisalpha = 1 - 1 / tempc0;
						thisbeta = 1 / tempc0;
					}
					else {
						thisalpha = _alpha;
						thisbeta = _beta;
					}
					fi->second.ms0 = thisalpha * (fi->second.ms0) + thisbeta * pow(v, 2);
					//fi->second.v0 = (1 - _beta) * (fi->second.v0) + (1 - _beta) * _beta * pow(fi->second.m0 - v, 2);
					fi->second.m0 = thisalpha * (fi->second.m0) + v * thisbeta;
					fi->second.w0 = _alpha * (fi->second.w0) + _beta;
					fi->second.ms1 = _alpha * (fi->second.ms1); //+ (1 - _beta) * _beta * pow(fi->second.m1, 2);
					//fi->second.v1 = pow((1 - _beta), 2) * (fi->second.v1); //+ (1 - _beta) * _beta * pow(fi->second.m1, 2);
					fi->second.m1 = _alpha * (fi->second.m1);
					fi->second.w1 = _alpha * (fi->second.w1);
				}
			}
		}
	}//end of each feature
	c1 = tempc1, c0 = tempc0;
	stopT = high_resolution_clock::now();
	binTime += stopT - startT;
	//// ctime() used to give the present time 
	//printf("\ttime of TrainSummary: %f\n", (stopT - startT).count());
	//fflush(stdout);
}

template<typename FType, typename DType, typename IType>
void MoveAVGDriftFixP<FType, DType, IType>::Finalize(vector<double>& fishscore, vector<double>& tscore, DType& bTime, DType& sTime) {
	double n = c1 + c0;
	int totalf = (int)sketch_collections.size();
	//using LabelEntry = LabelEntry<float, double, int>;
	for (int i = 0; i < totalf; ++i) {
		startT = high_resolution_clock::now();
		std::unordered_map<int, DriftEntry<DType>>::iterator fi = sketch_collections.find(i);


		//********t score*************
		startT = high_resolution_clock::now();
		double m1, m0, v1, v0, m, n0, n1;
		m1 = fi->second.m1;
		m0 = fi->second.m0;
		v1 = fi->second.ms1 - pow(m1, 2);
		v0 = fi->second.ms0 - pow(m0, 2);
		n1 = fi->second.w1;
		n0 = fi->second.w0;

		if (v1 + v0 > 0)
			tscore.push_back(abs(m1 - m0) / sqrt(v1 * n1 + v0 * n0));
		else
			tscore.push_back(0);

		//********fisher*************
		//m = (m1 * n1 + m0 * n0) / (n1 + n0);
		m = m1 * n1 + m0 * n0;
		if (v1 == 0 && v0 == 0)
			fishscore.push_back(0);
		else
			fishscore.push_back(((m1 - m) * (m1 - m) / n1 + (m0 - m) * (m0 - m) / n0) / (v1 / n1 + v0 / n0));
		//fishscore.push_back((n1 * (m1 - m) * (m1 - m) + n0 * (m0 - m) * (m0 - m)) / (n1 * v1 + n0 * v0));

		stopT = high_resolution_clock::now();
		scoreTime += stopT - startT;
	}

	bTime = binTime.count();
	sTime = scoreTime.count();
	//// ctime() used to give the present time 
	//time_t my_time = time(NULL);
	//printf("\ttime of TrainSummary: %f\n", (stopT - startT).count());
	//fflush(stdout);
	//std::unordered_map<int, std::vector<NoneDriftQSketch>>().swap(sketch_collections);
}

//================sparse no drift===================
template<typename FType, typename DType, typename IType, typename CType>
void MoveAVGUnfixP<FType, DType, IType, CType>::InitFiles(CType* path, CType* prefix, CType* extension, IType totalfiles) {
	_path = path;
	_prefix = prefix;
	_extension = extension;
	_totalfiles = totalfiles;
	d = 0; penaltimes = 0;
}

template<typename FType, typename DType, typename IType, typename CType>
int MoveAVGUnfixP<FType, DType, IType, CType>::TrainSummary() {

	for (d = 0; d < _totalfiles; d++)
	{
		debug6 = std::chrono::duration<double, std::milli>::zero();
		debug9 = std::chrono::duration<double, std::milli>::zero();
		//printf("file %d\n", d);
		PySys_WriteStdout("file %d\n", d);
		PyRun_SimpleString("import sys; sys.stdout.flush()");
		/*printf("varsize %d\n", vars.size());
		fflush(stdout);*/
		PySys_WriteStdout("\tvarsize %d\n", vars.size());
		PyRun_SimpleString("import sys; sys.stdout.flush()");
		sprintf(name, "%s/%s%d.%s", _path, _prefix, d, _extension);
		char line[100000];
		FILE* f = fopen(name, "rt");
		if (f == 0)
			return false;
		nrows = 0;
		while (!feof(f)) {
			nrows++;
			int head = 1, label;
			if (fgets(line, 100000, f) == 0)
				break;

			char* end_str;
			char* token = strtok_s(line, " ", &end_str);
			while (token != NULL) {
				debug4 = high_resolution_clock::now();
				startT = high_resolution_clock::now();
				if (head == 1) {
					label = std::stoi(token);
					//Yid.push_back(label);
					if (label == 1)
						c1++;
					else
						c0++;
					head = 0;
				}
				else {
					char* end_token;
					char* smalltoken = strtok_s(token, ":", &end_token);
					int idx = std::stoi(smalltoken);
					smalltoken = strtok_s(NULL, ":", &end_token);
					double v = (double)std::stod(smalltoken);
					//if (idx != 2) {//debug
					//	token = strtok_s(NULL, " ", &end_str);
					//	continue; 
					//}
					vars.insert(idx);
					// unlike other combinations, here we change how we use Entry without redefine it. we use m1,m0 to store sum, and ms1,ms0 to store sum of square
					if (label == 1) {
						std::unordered_map<int, Entry<DType>>::iterator fi = sketch_collections.find(idx);
						if (fi == sketch_collections.end()) {
							Entry<DType> tempentry = Entry<DType>(0, 0, v, pow(v, 2));
							sketch_collections.insert(std::unordered_map<int, Entry<DType>>::value_type(idx, tempentry));
						}
						else {
							//if (c1 >= 2) 
							fi->second.ms1 = fi->second.ms1 + pow(v, 2);
							fi->second.m1 = fi->second.m1 + v;
						}
					}
					else {
						std::unordered_map<int, Entry<DType>>::iterator fi = sketch_collections.find(idx);
						if (fi == sketch_collections.end()) {
							Entry<DType> tempentry = Entry<DType>(v, pow(v, 2), 0, 0);
							sketch_collections.insert(std::unordered_map<int, Entry<DType>>::value_type(idx, tempentry));
						}
						else {
							//if (c0 >= 2) 
							fi->second.ms0 = fi->second.ms0 + pow(v, 2);
							fi->second.m0 = fi->second.m0 + v;
						}
					}					

				}
				token = strtok_s(NULL, " ", &end_str);
				debug5 = high_resolution_clock::now();
				debug6 += debug5 - debug4;
				//for not mentioned features
				//std::unordered_map<int, std::pair<std::pair<std::vector<float>, std::vector<int>>, std::vector<DriftQSketch>>>::iterator fi;
			}
			delete[] token;
			debug8 = high_resolution_clock::now();
			debug9 += debug8 - debug7;
		}
		fclose(f);

		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//printf("\ttime of train current batch: %f\n", debug6.count());
		//fflush(stdout);
		////printf("\ttime of fill empty feature: %f\n", debug9.count());
		////mexEvalString("drawnow");
		////end of file
	}
	return (int)vars.size();
}

template<typename FType, typename DType, typename IType, typename CType>
void MoveAVGUnfixP<FType, DType, IType, CType>::Finalize(double* fishscore, double* tscore, std::set<int>& varout, DType& bTime, DType& sTime) {
	double n = c1 + c0;
	int si = 0;
	//using LabelEntry = LabelEntry<float, double, int>;
	for (std::set<int>::iterator vi = vars.begin(); vi != vars.end(); ++vi) {
		//startT = high_resolution_clock::now();
		std::unordered_map<int, Entry<DType>>::iterator fi = sketch_collections.find(*vi);
		
		startT = high_resolution_clock::now();
		double m1, m0, v1, v0, m;
		m1 = fi->second.m1/c1;
		m0 = fi->second.m0/c0;
		v1 = (fi->second.ms1 / c1) - pow(m1, 2);
		v0 = (fi->second.ms0 / c0) - pow(m0, 2);
		sketch_collections.erase(fi);

		//********t score*************
		if (v1 + v0 > 0)
			tscore[si] = abs(m1 - m0) / sqrt(v1 / c1 + v0 / c0);
		else
			tscore[si] = 0;

		//********fisher*************
		m = (m1 * c1 + m0 * c0) / (c1 + c0);
		if (v1 == 0 && v0 == 0)
			fishscore[si] = 0;
		else
			fishscore[si] = (c1 * (m1 - m) * (m1 - m) + c0 * (m0 - m) * (m0 - m)) / (c1 * v1 + c0 * v0);

		si++;
		stopT = high_resolution_clock::now();
		scoreTime += stopT - startT;
	}

	bTime = binTime.count();
	sTime = scoreTime.count();

	varout = vars;
}


//================sparse drift===================
template<typename FType, typename DType, typename IType, typename CType>
void MoveAVGDriftUnfixP<FType, DType, IType, CType>::InitFiles(CType* path, CType* prefix, CType* extension, IType totalfiles, double alpha, double beta) {
	_path = path;
	_prefix = prefix;
	_extension = extension;
	_totalfiles = totalfiles;
	_beta = beta;
	_alpha = alpha; d = 0; penaltimes = 0;
}

template<typename FType, typename DType, typename IType, typename CType>
int MoveAVGDriftUnfixP<FType, DType, IType, CType>::TrainSummary(double batchalpha) {

	for (d = 0; d < _totalfiles; d++)
	{
		debug6 = std::chrono::duration<double, std::milli>::zero();
		debug9 = std::chrono::duration<double, std::milli>::zero();
		//printf("file %d\n", d);
		PySys_WriteStdout("file %d\n", d);
		PyRun_SimpleString("import sys; sys.stdout.flush()");
		/*printf("varsize %d\n", vars.size());
		fflush(stdout);*/
		PySys_WriteStdout("\tvarsize %d\n", vars.size());
		PyRun_SimpleString("import sys; sys.stdout.flush()");
		sprintf(name, "%s/%s%d.%s", _path, _prefix, d, _extension);
		char line[100000];
		FILE* f = fopen(name, "rt");
		if (f == 0)
			return false;
		nrows = 0;
		while (!feof(f)) {
			nrows++;
			int head = 1, label;
			if (fgets(line, 100000, f) == 0)
				break;

			char* end_str;
			char* token = strtok_s(line, " ", &end_str);
			while (token != NULL) {
				debug4 = high_resolution_clock::now();
				startT = high_resolution_clock::now();
				if (head == 1) {
					label = std::stoi(token);
					//Yid.push_back(label);
					if (label == 1)
						c1++;
					else
						c0++;
					head = 0;
				}
				else {
					char* end_token;
					char* smalltoken = strtok_s(token, ":", &end_token);
					int idx = std::stoi(smalltoken);
					smalltoken = strtok_s(NULL, ":", &end_token);
					double v = (double)std::stod(smalltoken);
					//if (idx != 2) {//debug
					//	token = strtok_s(NULL, " ", &end_str);
					//	continue; 
					//}
					vars.insert(idx);
					if (label == 1) {
						std::unordered_map<int, std::pair<std::vector<int>, DriftEntry<DType>>>::iterator fi = sketch_collections.find(idx);
						if (fi == sketch_collections.end()) {
							DriftEntry<DType> tempentry;
							if (c0 + c1 == 1) {
								tempentry = DriftEntry<DType>(0, 0, 0, v, pow(v,2), 1);
							}
							else {
								double thisalpha, thisbeta;
								if (_alpha == 1 && _beta == 1 && c1 != 0) {
									thisalpha = 1 - 1 / c1;
									thisbeta = 1 / c1;
								}
								else {
									thisalpha = _alpha;
									thisbeta = _beta;
								}
								tempentry = DriftEntry<DType>(0, 0, _alpha * generalweight[0], thisbeta * v, thisbeta * pow(v,2), _alpha * generalweight[1] + _beta);
							}
							std::pair<std::vector<int>, DriftEntry<DType>> entryVector;
							entryVector.first.push_back(c0);//number of instances until last none 0 value for label 0
							entryVector.first.push_back(c1);//number of instances until last none 0 value for label 1
							entryVector.first.push_back(penaltimes);//penalty performed
							//if (c0 + c1 == 1) {
							//	current_sketch.PushSparse(label, v, coverage, (float)weight);
							//	adjustcount = 1;
							//}
							//else {
							//	if (label == 1) {
							//		current_sketch.PushSparse(0, 0, c0 * coverage, generalweight[0]);
							//		current_sketch.PushSparse(1, 0, (c1 - 1) * coverage, generalweight[1]);
							//	}
							//	else {
							//		current_sketch.PushSparse(0, 0, (c0 - 1) * coverage, generalweight[0]);
							//		current_sketch.PushSparse(1, 0, c1 * coverage, generalweight[1]);
							//	}
							//	current_sketch.PushSparse(label, v, coverage, (float)weight);
							//	//adjustcount = c0 + c1 + 1;
							//	adjustcount = 2;
							//}
							entryVector.second = tempentry;
							sketch_collections.insert(std::unordered_map<int, std::pair<std::vector<int>, DriftEntry<DType>>>::value_type(idx, entryVector));
						}
						else {
							//what's last record?????????
							int lastrecord0 = fi->second.first[0];
							int lastrecord1 = fi->second.first[1];
							if (c0 + c1 - lastrecord0 - lastrecord1 - 1 != 0) {//lebel==1
					/*			int k0 = c0 - lastrecord0;
								int k1 = c1 - lastrecord1 - 1;*/
								if (c1 - lastrecord1 - 1 > 0) {
									fi->second.second.ms1 = ((double)lastrecord1 / (c1 - 1)) * (fi->second.second.ms1);
									fi->second.second.m1 = ((double)lastrecord1 / (c1 - 1)) * (fi->second.second.m1);
									fi->second.second.w1 = tower1.back();
								}
								if (c0 - lastrecord0 > 0) {
									fi->second.second.ms0 = ((double)lastrecord0 / c0) * (fi->second.second.ms0);
									fi->second.second.m0 = ((double)lastrecord0 / c0) * (fi->second.second.m0);
									fi->second.second.w0 = tower0.back();
								}
								if (penaltimes - fi->second.first.back() >= 1 && batchalpha) {
									int expon = penaltimes - fi->second.first.back();
									fi->second.second.ms1 = exp(expon * log(batchalpha)) * (fi->second.second.ms1);
									fi->second.second.m1 = exp(expon * log(batchalpha)) * (fi->second.second.m1);
									fi->second.second.ms0 = exp(expon * log(batchalpha)) * (fi->second.second.ms0);
									fi->second.second.m0 = exp(expon * log(batchalpha)) * (fi->second.second.m0);
									fi->second.first.back() = penaltimes;
								}
								//for (std::vector<int>::iterator l = Yid.begin() + lastrecord0 + lastrecord1; l != Yid.end() - 1; ++l) {
								//	if (*l == 1) {
								//		//c1++;
								//		fi->second.second.ms1 = (1 - _beta) * (fi->second.second.ms1) + _beta * pow(0, 2);
								//		fi->second.second.m1 = (1 - _beta) * (fi->second.second.m1) + 0 * _beta;
								//		fi->second.second.w1 = (1 - _beta) * (fi->second.second.w1) + _beta;
								//		fi->second.second.ms0 = (1 - _beta) * (fi->second.second.ms0);
								//		fi->second.second.m0 = (1 - _beta) * (fi->second.second.m0);
								//		fi->second.second.w0 = (1 - _beta) * (fi->second.second.w0);
								//	}
								//	else {
								//		//c0++;				
								//		fi->second.second.ms0 = (1 - _beta) * (fi->second.second.ms0) + _beta * pow(0, 2);
								//		fi->second.second.m0 = (1 - _beta) * (fi->second.second.m0) + 0 * _beta;
								//		fi->second.second.w0 = (1 - _beta) * (fi->second.second.w0) + _beta;
								//		fi->second.second.ms1 = (1 - _beta) * (fi->second.second.ms1); //+ (1 - _beta) * _beta * pow(fi->second.m1, 2);
								//		fi->second.second.m1 = (1 - _beta) * (fi->second.second.m1);
								//		fi->second.second.w1 = (1 - _beta) * (fi->second.second.w1);
								//	}
								//}
							}
							if (d != 0 && nrows == 1 && batchalpha) {
								fi->second.second.ms1 = batchalpha * (fi->second.second.ms1);
								fi->second.second.m1 = batchalpha * (fi->second.second.m1);
								fi->second.second.w1 = batchalpha * (fi->second.second.w1);
								fi->second.second.ms0 = batchalpha * (fi->second.second.ms0);
								fi->second.second.m0 = batchalpha * (fi->second.second.m0);
								fi->second.second.w0 = batchalpha * (fi->second.second.w0);
								fi->second.first.back() += 1;
							}
							double thisalpha, thisbeta;
							if (_alpha == 1 && _beta == 1 && c1 != 0) {
								thisalpha = 1 - 1 / c1;
								thisbeta = 1 / c1;
							}
							else {
								thisalpha = _alpha;
								thisbeta = _beta;
							}
							fi->second.second.ms1 = thisalpha * (fi->second.second.ms1) + thisbeta * pow(v, 2);
							fi->second.second.m1 = thisalpha * (fi->second.second.m1) + v * thisbeta;
							fi->second.second.w1 = _alpha * (fi->second.second.w1) + _beta;
							fi->second.second.ms0 = _alpha * (fi->second.second.ms0);
							fi->second.second.m0 = _alpha * (fi->second.second.m0);
							fi->second.second.w0 = _alpha * (fi->second.second.w0);
							fi->second.first[0] = c0;
							fi->second.first[1] = c1;
							
						}
					}
					else {
						std::unordered_map<int, std::pair<std::vector<int>, DriftEntry<DType>>>::iterator fi = sketch_collections.find(idx);
						if (fi == sketch_collections.end()) {
							DriftEntry<DType> tempentry;
							if (c0 + c1 == 1) {
								tempentry = DriftEntry<DType>(v, pow(v, 2), 1, 0, 0, 0);
							}
							else {
								double thisalpha, thisbeta;
								if (_alpha == 1 && _beta == 1 && c0 != 0) {
									thisalpha = 1 - 1 / c0;
									thisbeta = 1 / c0;
								}
								else {
									thisalpha = _alpha;
									thisbeta = _beta;
								}
								tempentry = DriftEntry<DType>(thisbeta * v, thisbeta * pow(v,2), _alpha * generalweight[0] + _beta, 0, 0, _alpha * generalweight[1]);
							}
							std::pair<std::vector<int>, DriftEntry<DType>> entryVector;
							entryVector.first.push_back(c0);//number of instances until last none 0 value for label 0
							entryVector.first.push_back(c1);//number of instances until last none 0 value for label 1
							entryVector.second = tempentry;
							sketch_collections.insert(std::unordered_map<int, std::pair<std::vector<int>, DriftEntry<DType>>>::value_type(idx, entryVector));
						}
						else {
							//what's last record?????????
							int lastrecord0 = fi->second.first[0];
							int lastrecord1 = fi->second.first[1];
							if (c0 + c1 - lastrecord0 - lastrecord1 - 1 != 0) {//label==0
							/*	int k0 = c0 - lastrecord0 - 1;
								int k1 = c1 - lastrecord1;*/
								if (c1 - lastrecord1 > 0) {
									fi->second.second.ms1 = ((double)lastrecord1 / c1) * (fi->second.second.ms1);
									fi->second.second.m1 = ((double)lastrecord1 / c1) * (fi->second.second.m1);
									fi->second.second.w1 = tower1.back();
								}
								if (c0 - lastrecord0 - 1 > 0) {
									fi->second.second.ms0 = ((double)lastrecord0 / (c0 - 1)) * (fi->second.second.ms0);
									fi->second.second.m0 = ((double)lastrecord0 / (c0 - 1)) * (fi->second.second.m0);
									fi->second.second.w0 = tower0.back();
								}
								if (penaltimes - fi->second.first.back() >= 1 && batchalpha) {
									int expon = penaltimes - fi->second.first.back();
									fi->second.second.ms1 = exp(expon * log(batchalpha)) * (fi->second.second.ms1);
									fi->second.second.m1 = exp(expon * log(batchalpha)) * (fi->second.second.m1);
									fi->second.second.ms0 = exp(expon * log(batchalpha)) * (fi->second.second.ms0);
									fi->second.second.m0 = exp(expon * log(batchalpha)) * (fi->second.second.m0);
									fi->second.first.back() = penaltimes;
								}
								//for (std::vector<int>::iterator l = Yid.begin() + lastrecord0 + lastrecord1; l != Yid.end() - 1; ++l) {
								//	if (*l == 1) {
								//		//c1++;
								//		fi->second.second.ms1 = (1 - _beta) * (fi->second.second.ms1) + _beta * pow(0, 2);
								//		fi->second.second.m1 = (1 - _beta) * (fi->second.second.m1) + 0 * _beta;
								//		fi->second.second.w1 = (1 - _beta) * (fi->second.second.w1) + _beta;
								//		fi->second.second.ms0 = (1 - _beta) * (fi->second.second.ms0);
								//		fi->second.second.m0 = (1 - _beta) * (fi->second.second.m0);
								//		fi->second.second.w0 = (1 - _beta) * (fi->second.second.w0);
								//	}
								//	else {
								//		//c0++;				
								//		fi->second.second.ms0 = (1 - _beta) * (fi->second.second.ms0) + _beta * pow(0, 2);
								//		fi->second.second.m0 = (1 - _beta) * (fi->second.second.m0) + 0 * _beta;
								//		fi->second.second.w0 = (1 - _beta) * (fi->second.second.w0) + _beta;
								//		fi->second.second.ms1 = (1 - _beta) * (fi->second.second.ms1); //+ (1 - _beta) * _beta * pow(fi->second.m1, 2);
								//		fi->second.second.m1 = (1 - _beta) * (fi->second.second.m1);
								//		fi->second.second.w1 = (1 - _beta) * (fi->second.second.w1);
								//	}
								//}
							}
							if (d != 0 && nrows == 1 && batchalpha) {
								fi->second.second.ms1 = batchalpha * (fi->second.second.ms1);
								fi->second.second.m1 = batchalpha * (fi->second.second.m1);
								fi->second.second.w1 = batchalpha * (fi->second.second.w1);
								fi->second.second.ms0 = batchalpha * (fi->second.second.ms0);
								fi->second.second.m0 = batchalpha * (fi->second.second.m0);
								fi->second.second.w0 = batchalpha * (fi->second.second.w0);
								fi->second.first.back() += 1;
							}
							double thisalpha, thisbeta;
							if (_alpha == 1 && _beta == 1 && c0 != 0) {
								thisalpha = 1 - 1 / c0;
								thisbeta = 1 / c0;
							}
							else {
								thisalpha = _alpha;
								thisbeta = _beta;
							}
							fi->second.second.ms0 = thisalpha * (fi->second.second.ms0) + thisbeta * pow(v, 2);
							fi->second.second.m0 = thisalpha * (fi->second.second.m0) + v * thisbeta;
							fi->second.second.w0 = _alpha * (fi->second.second.w0) + _beta;
							fi->second.second.ms1 = _alpha * (fi->second.second.ms1); //+ (1 - _beta) * _beta * pow(fi->second.m1, 2);
							fi->second.second.m1 = _alpha * (fi->second.second.m1);
							fi->second.second.w1 = _alpha * (fi->second.second.w1);
							fi->second.first[0] = c0;
							fi->second.first[1] = c1;
						}
					}

				}
				token = strtok_s(NULL, " ", &end_str);
				debug5 = high_resolution_clock::now();
				debug6 += debug5 - debug4;
				//for not mentioned features
				//std::unordered_map<int, std::pair<std::pair<std::vector<float>, std::vector<int>>, std::vector<DriftQSketch>>>::iterator fi;
			}
			delete[] token;
			if (label == 1) {
				//c1++;
				if (c0 + c1 == 1) {
					generalweight[1] = 1;
				}
				else {
					generalweight[1] = _alpha * generalweight[1] + _beta;
				}
				generalweight[0] = _alpha * generalweight[0];
				if (d != 0 && nrows == 1 && batchalpha) {
					generalweight[0] = batchalpha * generalweight[0];
					generalweight[1] = batchalpha * generalweight[1];
					penaltimes++;
				}
				tower1.push_back(generalweight[1]);
				tower0.push_back(generalweight[0]);
			}
			else {
				//c0++;
				if (c0 + c1 == 1) {
					generalweight[0] = 1;
				}
				else {
					generalweight[0] = _alpha * generalweight[0] + _beta;
				}
				generalweight[1] = _alpha * generalweight[1];
				if (d != 0 && nrows == 1 && batchalpha) {
					generalweight[0] = batchalpha * generalweight[0];
					generalweight[1] = batchalpha * generalweight[1];
					penaltimes++;
				}
				tower0.push_back(generalweight[0]);
				tower1.push_back(generalweight[1]);
			}
			debug8 = high_resolution_clock::now();
			debug9 += debug8 - debug7;
		}
		fclose(f);

		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//printf("\ttime of train current batch: %f\n", debug6.count());
		//fflush(stdout);
		////printf("\ttime of fill empty feature: %f\n", debug9.count());
		////mexEvalString("drawnow");
		////end of file
	}
	return (int)vars.size();
}

template<typename FType, typename DType, typename IType, typename CType>
void MoveAVGDriftUnfixP<FType, DType, IType, CType>::Finalize(double* fishscore, double* tscore, std::set<int>& varout, DType& bTime, DType& sTime, double batchalpha) {
	double n = c1 + c0;
	int si = 0;
	//using LabelEntry = LabelEntry<float, double, int>;
	for (std::set<int>::iterator vi = vars.begin(); vi != vars.end(); ++vi) {
		startT = high_resolution_clock::now();
		std::unordered_map<int, std::pair<std::vector<int>, DriftEntry<DType>>>::iterator fi = sketch_collections.find(*vi);

		int lastrecord0 = fi->second.first[0];
		int lastrecord1 = fi->second.first[1];
		if (c0 + c1 - lastrecord0 - lastrecord1 > 0) {
	/*		int k0 = c0 + c1 - lastrecord0 - lastrecord1;
			int k1 = c0 + c1 - lastrecord0 - lastrecord1;*/
			fi->second.second.ms1 = ((double)lastrecord1 / c1) * (fi->second.second.ms1);
			fi->second.second.m1 = ((double)lastrecord1 / c1) * (fi->second.second.m1);
			fi->second.second.w1 = tower1.back();
			fi->second.second.ms0 = ((double)lastrecord0 / c0) * (fi->second.second.ms0);
			fi->second.second.m0 = ((double)lastrecord0 / c0) * (fi->second.second.m0);
			fi->second.second.w0 = tower0.back();
			if (penaltimes - fi->second.first.back() >= 1 && batchalpha) {
				int expon = penaltimes - fi->second.first.back();
				fi->second.second.ms1 = exp(expon * log(batchalpha)) * (fi->second.second.ms1);
				fi->second.second.m1 = exp(expon * log(batchalpha)) * (fi->second.second.m1);
				fi->second.second.ms0 = exp(expon * log(batchalpha)) * (fi->second.second.ms0);
				fi->second.second.m0 = exp(expon * log(batchalpha)) * (fi->second.second.m0);
				fi->second.first.back() = penaltimes;
			}
			//for (std::vector<int>::iterator l = Yid.begin() + lastrecord0 + lastrecord1; l != Yid.end(); ++l) {
			//	if (*l == 1) {
			//		//c1++;
			//		fi->second.second.ms1 = (1 - _beta) * (fi->second.second.ms1) + _beta * pow(0, 2);
			//		fi->second.second.m1 = (1 - _beta) * (fi->second.second.m1) + 0 * _beta;
			//		fi->second.second.w1 = (1 - _beta) * (fi->second.second.w1) + _beta;
			//		fi->second.second.ms0 = (1 - _beta) * (fi->second.second.ms0);
			//		fi->second.second.m0 = (1 - _beta) * (fi->second.second.m0);
			//		fi->second.second.w0 = (1 - _beta) * (fi->second.second.w0);
			//	}
			//	else {
			//		//c0++;				
			//		fi->second.second.ms0 = (1 - _beta) * (fi->second.second.ms0) + _beta * pow(0, 2);
			//		fi->second.second.m0 = (1 - _beta) * (fi->second.second.m0) + 0 * _beta;
			//		fi->second.second.w0 = (1 - _beta) * (fi->second.second.w0) + _beta;
			//		fi->second.second.ms1 = (1 - _beta) * (fi->second.second.ms1); //+ (1 - _beta) * _beta * pow(fi->second.m1, 2);
			//		fi->second.second.m1 = (1 - _beta) * (fi->second.second.m1);
			//		fi->second.second.w1 = (1 - _beta) * (fi->second.second.w1);
			//	}
			//}
		}
		startT = high_resolution_clock::now();
		double m1, m0, v1, v0, m, n0, n1;
		m1 = fi->second.second.m1;
		m0 = fi->second.second.m0;
		v1 = fi->second.second.ms1 - pow(m1, 2);
		v0 = fi->second.second.ms0 - pow(m0, 2);
		n1 = fi->second.second.w1;
		n0 = fi->second.second.w0;
		sketch_collections.erase(fi);

		//********t score*************
		if (v1 + v0 > 0)
			tscore[si] = (abs(m1 - m0) / sqrt(v1 * n1 + v0 * n0));
		else
			tscore[si] = (0);

		//********fisher*************
		//m = (m1 * n1 + m0 * n0) / (n1 + n0);
		m = m1 * n1 + m0 * n0;
		if (v1 == 0 && v0 == 0)
			fishscore[si] = 0;
		else
			fishscore[si] = ((m1 - m) * (m1 - m) / n1 + (m0 - m) * (m0 - m) / n0) / (v1 / n1 + v0 / n0);
		//fishscore.push_back((n1 * (m1 - m) * (m1 - m) + n0 * (m0 - m) * (m0 - m)) / (n1 * v1 + n0 * v0));
		si++;
		stopT = high_resolution_clock::now();
		scoreTime += stopT - startT;
	}

	bTime = binTime.count();
	sTime = scoreTime.count();
	varout = vars;
	//// ctime() used to give the present time 
	//time_t my_time = time(NULL);
	//printf("\ttime of TrainSummary: %f\n", (stopT - startT).count());
	//fflush(stdout);
	//std::unordered_map<int, std::vector<NoneDriftQSketch>>().swap(sketch_collections);
}


#endif