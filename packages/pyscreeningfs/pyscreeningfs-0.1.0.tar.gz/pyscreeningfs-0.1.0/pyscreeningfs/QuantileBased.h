/*
* Code Contributors
* Mingyuan Wang
*/
#ifndef QUANTBASED_H_
#define QUANTBASED_H_
#include <iostream>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <vector>
#include <cmath>
#include "quantile_nop_binary.h"
#include "quantile_drift.h"
#include <chrono> 
#include <unordered_map> 
#include <time.h>


using namespace std::chrono;
using namespace std;
using NoneDriftQSketch = none_drift_summary::WXQuantileSketch<float, int>;
using DriftQSketch = drift_summary::WXQuantileSketch<float, double, int>;

template<typename FType, typename DType, typename IType>
class OnlineQuantileNPknown {
private:
	vector<double> _x, _y;
	IType _batchSize, batchnum, _P;
	int startsummary, stream_seg, stream_start, stream_end, initSize, backup_start, backup_end, backup_seg, backup_initsize, backup_startsumm, batchend;
	std::unordered_map<int, std::vector<NoneDriftQSketch>> sketch_collections;
	//const int _weight = 1;
	//high_resolution_clock::time_point startT, stopT;
	//std::chrono::duration<double, std::milli> binTime, scoreTime;
protected:
	IType _factor, _numbin;
	int c1, c0;
	int _weight = 1;
	high_resolution_clock::time_point startT, stopT;
	std::chrono::duration<double, std::milli> binTime, scoreTime;

public:
	OnlineQuantileNPknown(IType factor, IType numbin, IType P) {
		_factor = factor;
		_numbin = numbin;
		_P = P;
		c1 = 0;
		c0 = 0;
		startsummary = 0;
		//seg count start with one
		stream_seg = 0;
		stream_start = (int)(pow(2, stream_seg) - 1) * _factor;
		stream_end = (int)(pow(2, stream_seg + 1) - 1) * _factor - 1;
		initSize = (int)pow(2, stream_seg) * _factor;
		backup_start = stream_start;
		backup_end = stream_end;
		backup_seg = stream_seg;
		backup_initsize = initSize;
		backup_startsumm = startsummary;
	}

	class LabelEntry {
	public:
		/*! \brief minimum rank */
		IType rmin;
		/*! \brief maximum rank */
		IType rmax;
		/*! \brief the _weight of label1 */
		DType w0;
		/*! \brief the _weight of label0 */
		DType w1;
		/*! \brief the value of data */
		DType value;

		LabelEntry() {}  // NOLINT
						 // constructor
		LabelEntry(IType rmin, IType rmax, DType w0, DType w1, DType value)
			: rmin(rmin), rmax(rmax), w0(w0), w1(w1), value(value) {}
	};

	void stuffBatch(vector<double>& x, vector<double>& y, IType batchSize);

	void TrainSummary();

	void GetSegSummary(NoneDriftQSketch& segS, std::vector<NoneDriftQSketch, std::allocator<NoneDriftQSketch>>* sketch);

	template<typename Vtype>
	void GetBinVector(Vtype& cl0, Vtype& cl1, NoneDriftQSketch::SummaryContainer& insummary, int n);

	template<typename Vtype>
	void GetScore(double& chi2, double& gini, double& mi, Vtype& cl0, Vtype& cl1, int c0, int c1);

	void Finalize(double* binMatrix, double* miscore, double* chi2score, double* giniscore, DType& bTime, DType& sTime);

	//void FinalizeInterv(vector<double>& miscore, vector<double>& chi2score, vector<double>& giniscore, DType& bTime, DType& sTime);
	void FinalizeInterv(double* miscore, double* chi2score, double* giniscore, DType& bTime, DType& sTime, IType outnum, IType fnum);
};

template<typename FType, typename DType, typename IType>
class OnlineQuantileNPknownDrift : public OnlineQuantileNPknown<FType, DType, IType> {
protected:
	vector<double> _x, _y;
	IType _batchSize, batchnum, _P;
	int startsummary, stream_seg, stream_start, stream_end, initSize, backup_start, backup_end, backup_seg, backup_initsize, backup_startsumm, batchend;
	std::unordered_map<int, std::vector<DriftQSketch>> sketch_collections;
	double _alpha, _beta;
	//const int _weight = 1;
	//high_resolution_clock::time_point startT, stopT;
	//std::chrono::duration<double, std::milli> binTime, scoreTime;

public:
	using LabelEntry = typename OnlineQuantileNPknown<FType, DType, IType>::LabelEntry;
	OnlineQuantileNPknownDrift(IType factor, IType numbin, IType P) : OnlineQuantileNPknown(0, 0, 0) {
		_factor = factor;
		_numbin = numbin;
		_P = P;
		c1 = 0;
		c0 = 0;
		startsummary = 0;
		//seg count start with one
		stream_seg = 0;
		stream_start = (int)(pow(2, stream_seg) - 1) * _factor;
		stream_end = (int)(pow(2, stream_seg + 1) - 1) * _factor - 1;
		initSize = (int)pow(2, stream_seg) * _factor;
		backup_start = stream_start;
		backup_end = stream_end;
		backup_seg = stream_seg;
		backup_initsize = initSize;
		backup_startsumm = startsummary;
	}

	void stuffBatch(vector<double>& x, vector<double>& y, IType batchSize, double alpha, double beta);

	void BatchPenal(std::unordered_map<int, std::vector<DriftQSketch>>::iterator inputfi, double batchalpha);

	void TrainSummary(double batchadapt);

	void GetSegSummary(DriftQSketch& segS, std::vector<DriftQSketch, std::allocator<DriftQSketch>>* sketch, int seg);

	template<typename Vtype>
	void GetBinVector(Vtype& cl0, Vtype& cl1, DriftQSketch::SummaryContainer& insummary, int n);

	template<typename Vtype>
	void GetScore(double& chi2, double& gini, double& mi, Vtype& cl0, Vtype& cl1);

	void Finalize(double* binMatrix, double* miscore, double* chi2score, double* giniscore, DType& bTime, DType& sTime);

	void FinalizeInterv(vector<double>& miscore, vector<double>& chi2score, vector<double>& giniscore, DType& bTime, DType& sTime);
};

template<typename FType, typename DType, typename IType, typename CType>
class OnlineQuantileNPunknown : public OnlineQuantileNPknown<FType, DType, IType> {
protected:
	std::set<int> vars;
	char name[255], * _path, * _prefix, * _extension;
	int _totalfiles;// , c1, c0;
	//IType _factor, _numbin;
	std::unordered_map<int, std::pair<std::pair<std::vector<int>, std::vector<int>>, std::vector<NoneDriftQSketch>>> sketch_collections;
	//const int _weight = 1;
	//high_resolution_clock::time_point startT, stopT;
	//std::chrono::duration<double, std::milli> binTime, scoreTime;
public:
	OnlineQuantileNPunknown(IType factor, IType numbin) : OnlineQuantileNPknown(0, 0, 0) {
		_factor = factor;
		_numbin = numbin;
		c1 = 0;
		c0 = 0;
	}

	using LabelEntry = typename OnlineQuantileNPknown<FType, DType, IType>::LabelEntry;

	void InitFiles(CType* path, CType* prefix, CType* extension, IType totalfiles);

	int TrainSummary();

	void Finalize(double* binMatrix, double* miscore, double* chi2score, double* giniscore, std::set<int>& varout, DType& bTime, DType& sTime);
};

template<typename FType, typename DType, typename IType, typename CType>
class OnlineQuantileNPunknownDrift : public OnlineQuantileNPknown<FType, DType, IType> {
protected:
	std::set<int> vars;
	char name[255], * _path, * _prefix, * _extension;
	int _totalfiles, coverage, penaltimes, d, nrows;// , c1, c0;
	//IType _factor, _numbin;
	std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>> sketch_collections;
	//std::unordered_map<int, std::vector<DriftQSketch>> zeroweightcumulator;
	double _alpha, _beta;
	std::vector<double> generalweight, wtower0, wtower1;
	std::vector<int> Yid;
	//const int _weight = 1;
	//* debug parameter
	high_resolution_clock::time_point debug1, debug2, debug4, debug5, debug7, debug8, debug10, debug11;
	std::chrono::duration<double, std::milli> debug3, debug6, debug9, debug12;
public:
	OnlineQuantileNPunknownDrift(IType factor, IType numbin) : OnlineQuantileNPknown(0, 0, 0) {
		_factor = factor;
		_numbin = numbin;
		c1 = 0;
		c0 = 0;
		coverage = 1;
		generalweight.push_back(0.0);
		generalweight.push_back(0.0);
	}

	using LabelEntry = typename OnlineQuantileNPknown<FType, DType, IType>::LabelEntry;

	void InitFiles(CType* path, CType* prefix, CType* extension, IType totalfiles, double alpha, double beta);

	void BatchPenal(std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>>::iterator inputfi, double batchalpha);

	int TrainSummary(double batchalpha);

	void GetSegSummary(DriftQSketch& segS, std::pair<std::vector<int>, std::vector<DriftQSketch>>& context);

	void ChoisePush(std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>>::iterator thisfi, int& adjustcount, int label, double v, double batchalpha);

	template<typename Vtype>
	void GetBinVector(Vtype& cl0, Vtype& cl1, DriftQSketch::SummaryContainer& insummary, int n);

	template<typename Vtype>
	void GetScore(double& chi2, double& gini, double& mi, Vtype& cl0, Vtype& cl1);

	void Finalize(double* binMatrix, double* miscore, double* chi2score, double* giniscore, int* varout, DType& bTime, DType& sTime, double batchalpha);
};
//======================none sparse=================================
template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknown<FType, DType, IType>::stuffBatch(vector<double>& x, vector<double>& y, IType batchSize) {
	//startT = high_resolution_clock::now();
	batchend = batchSize;
	_x = x;
	_y = y;
	//// ctime() used to give the present time 
	//stopT = high_resolution_clock::now();
	//printf("\ttime of stuffBatch: %f\n", (stopT - startT).count());
	//fflush(stdout);
}

template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknown<FType, DType, IType>::TrainSummary() {
	startT = high_resolution_clock::now();
	for (int j = 0; j < _P; j++) {
		stream_start = backup_start;
		stream_seg = backup_seg;
		initSize = backup_initsize;
		stream_end = backup_end;
		startsummary = backup_startsumm;
		for (int i = 0; i < batchend; i++) {
			int col = j;
			int addre = batchend * j + i;
			double v = _x[addre];//n*j+i
			int label = (int)_y[i];
			if (col == 0) {
				if (label == 1) {
					c1++;
				}
				else {
					c0++;
				}
			}
			std::unordered_map<int, std::vector<NoneDriftQSketch>>::iterator fi = sketch_collections.find(col);
			if (fi == sketch_collections.end()) {
				NoneDriftQSketch current_sketch;
				std::vector<NoneDriftQSketch> sketchVector;
				current_sketch.Init(initSize, 1.0 / (_factor));
				current_sketch.Push(label, v, _weight);
				sketchVector.push_back(current_sketch);
				sketch_collections.insert(std::unordered_map<int, std::vector<NoneDriftQSketch>>::value_type(col, sketchVector));
			}
			else if (startsummary == 1) {
				if (stream_seg == 1) {
					NoneDriftQSketch current_sketch;
					current_sketch.Init(initSize, 1.0 / (_factor));
					current_sketch.Push(label, v, _weight);
					fi->second.push_back(current_sketch);
				}
				else {
					NoneDriftQSketch union_sketch;
					GetSegSummary(union_sketch, &fi->second);
					//put into first
					fi->second.front() = union_sketch;
					//inital second to new
					fi->second.back().Init(initSize, 1.0 / (_factor));
					fi->second.back().Push(label, v, _weight);
				}
				startsummary = 0;
			}
			else {
				fi->second.back().Push(label, v, _weight);
			}
			--stream_end;
			if (stream_end - stream_start + 1 == 0) {
				++stream_seg;
				stream_start = (int)(pow(2, stream_seg) - 1) * _factor;
				stream_end = (int)(pow(2, stream_seg + 1) - 1) * _factor - 1;
				initSize = (int)pow(2, stream_seg) * _factor;
				startsummary = 1;
			}
		}
		if (j == _P - 1) {
			backup_start = stream_start;
			backup_end = stream_end;
			backup_seg = stream_seg;
			backup_initsize = initSize;
			backup_startsumm = startsummary;
		}
	}//end of each feature
	stopT = high_resolution_clock::now();
	binTime += stopT - startT;
	//// ctime() used to give the present time 
	//printf("\ttime of TrainSummary: %f\n", (stopT - startT).count());
	//fflush(stdout);
}

template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknown<FType, DType, IType>::GetSegSummary(NoneDriftQSketch& segS, std::vector<NoneDriftQSketch, std::allocator<NoneDriftQSketch>>* sketch) {
	//combine last two summary
	NoneDriftQSketch::SummaryContainer frontSummary, backSummary;
	if (sketch->front().temp.data.size() == 0) {
		sketch->front().GetSummary(&frontSummary, 1.0 / (_factor));
		sketch->back().GetSummary(&backSummary, 1.0 / (_factor));
	}
	else {
		frontSummary = sketch->front().temp;
		sketch->back().GetSummary(&backSummary, 1.0 / (_factor));
	}
	segS.temp.SetCombine(frontSummary, backSummary);
}

template<typename FType, typename DType, typename IType>
template<typename Vtype>
void OnlineQuantileNPknown<FType, DType, IType>::GetBinVector(Vtype& cl0, Vtype& cl1, NoneDriftQSketch::SummaryContainer& insummary, int n) {
	double epsilonN = (double)1.0 / (_factor)*n;
	double est_bin_size = (double)n / _numbin;
	int current_bin = 0;
	double lastboundry = 0, boundry;
	int ispass = 0;
	LabelEntry lastentry = LabelEntry(0, 0, 0, 0, 0);
	//float aprev_rmin = 0, bprev_rmin = 0;

	float x1 = 0, x0 = 0;
	for (auto& s : insummary.data) {
		x0 += lastentry.w0;
		x1 += lastentry.w1;
		cl0[current_bin] += lastentry.w0;
		cl1[current_bin] += lastentry.w1;
		if (ispass == 1) {
			if (s.value != lastentry.value) {
				boundry = round((current_bin + 1) * est_bin_size);
				boundry = (s.rmin - boundry) > (boundry - lastentry.rmax) ? (lastentry.rmax) : (s.rmin);
				lastboundry = boundry;
				while (boundry - round((current_bin + 1) * est_bin_size) >= 0) {
					++current_bin;
				}
				ispass = 0;
			}
		}
		else if (s.rmin >= round((current_bin + 1) * est_bin_size)) {// || lastentry.rmax >= (current_bin + 1)*est_bin_size) {
			if (s.value != lastentry.value) {
				boundry = round((current_bin + 1) * est_bin_size);
				boundry = (s.rmin - boundry) > (boundry - lastentry.rmax) ? lastentry.rmax : s.rmin;//(s.rmin + lastentry.rmax) / 2;					
				lastboundry = boundry;
				while (boundry - round((current_bin + 1) * est_bin_size) >= 0) {
					++current_bin;
				}
			}
			else ispass = 1;
		}

		lastentry = LabelEntry(s.rmin, s.rmax, s.wmin0, s.wmin1, s.value);
	}
	cl0[current_bin] += lastentry.w0;
	cl1[current_bin] += lastentry.w1;
}

template<typename FType, typename DType, typename IType>
template<typename Vtype>
void OnlineQuantileNPknown<FType, DType, IType>::GetScore(double& chi2, double& gini, double& mi, Vtype& cl0, Vtype& cl1, int c0, int c1) {
	int nlc, nlc0, nlc1, n = c0 + c1;
	double nlc_hat1, nlc_hat0, part0, part1;

	for (int j = 0; j < _numbin; j++) {
		nlc1 = cl1[j];
		nlc0 = cl0[j];
		nlc = nlc1 + nlc0;
		nlc_hat0 = c0 * nlc / (double)n;
		nlc_hat1 = c1 * nlc / (double)n;
		if (nlc_hat0 == 0) part0 = 0; else part0 = (nlc0 - nlc_hat0) * (nlc0 - nlc_hat0) / nlc_hat0;
		if (nlc_hat1 == 0) part1 = 0; else part1 = (nlc1 - nlc_hat1) * (nlc1 - nlc_hat1) / nlc_hat1;
		chi2 += part0 + part1;
	}

	//Gini
	int ah = 0, bh = n, ah0 = 0, ah1 = 0, bh0 = c0, bh1 = c1;
	double  pah, pbh, pah0, pah1, pbh0, pbh1, parta, partb;
	vector<double> gini_column;
	//gini_column.reserve(_numbin);
	for (int j = 0; j < _numbin; j++) {
		if (ah == 0) parta = 0; else {
			pah = ah / (double)n;
			pah0 = ah0 / (double)ah;
			pah1 = ah1 / (double)ah;
			parta = pah * (1 - pow(pah0, 2) - pow(pah1, 2));
		}
		if (bh == 0) partb = 0; else {
			pbh = bh / (double)n;
			pbh0 = bh0 / (double)bh;
			pbh1 = bh1 / (double)bh;
			partb = pbh * (1 - pow(pbh0, 2) - pow(pbh1, 2));
		}
		gini_column.push_back((double)parta + partb);

		ah0 += cl0[j];
		ah1 += cl1[j];
		ah = ah0 + ah1;

		bh0 -= cl0[j];
		bh1 -= cl1[j];
		bh = bh1 + bh0;
	}
	gini = *std::min_element(gini_column.begin(), gini_column.end());

	//MI
	double px, py0 = c0 / (double)n, py1 = c1 / (double)n, pxy1, pxy0;

	for (int j = 0; j < _numbin; j++) {
		nlc1 = cl1[j];
		nlc0 = cl0[j];
		nlc = nlc1 + nlc0;
		px = nlc / (double)n;
		pxy0 = nlc0 / (double)n;
		pxy1 = nlc1 / (double)n;
		if (pxy0 == 0) part0 = 0; else part0 = pxy0 * log(pxy0 / (px * py0));
		if (pxy1 == 0) part1 = 0; else part1 = pxy1 * log(pxy1 / (px * py1));
		mi += part0 + part1;
	}
}

template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknown<FType, DType, IType>::Finalize(double* binMatrix, double* miscore, double* chi2score, double* giniscore, DType& bTime, DType& sTime) {
	int n = c1 + c0;
	int totalf = (int)sketch_collections.size();
	//using LabelEntry = LabelEntry<float, double, int>;
	for (int i = 0; i < totalf; ++i) {
		startT = high_resolution_clock::now();
		NoneDriftQSketch::SummaryContainer out;
		std::unordered_map<int, std::vector<NoneDriftQSketch>>::iterator fi = sketch_collections.find(i);
		if (fi->second.size() == 1) {
			fi->second.front().GetSummary(&out, 1.0 / (_factor));
		}
		else {
			NoneDriftQSketch::SummaryContainer frontSummary, backSummary;
			if (fi->second.front().temp.data.size() == 0) {
				fi->second.front().GetSummary(&frontSummary, 1.0 / (_factor));
			}
			else {
				frontSummary = fi->second.front().temp;
			}
			fi->second.back().GetSummary(&backSummary, 1.0 / (_factor));
			NoneDriftQSketch union_sketch;
			union_sketch.temp.SetCombine(frontSummary, backSummary);
			out = union_sketch.temp;
		}
		sketch_collections.erase(fi);
		vector<int> cl0(_numbin, 0), cl1(_numbin, 0);
		OnlineQuantileNPknown::GetBinVector(cl0, cl1, out, n);

		for (int b = 0; b < _numbin; ++b) {
			binMatrix[_numbin * 2 * i + b] = cl0[b];
			binMatrix[_numbin * 2 * i + b + _numbin] = cl1[b];
		}
		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//********end of sketch*************
		startT = high_resolution_clock::now();
		double chi2 = 0, gini = 0, mi = 0;
		OnlineQuantileNPknown::GetScore(chi2, gini, mi, cl0, cl1, c0, c1);

		chi2score[i] = chi2;
		giniscore[i] = gini;
		miscore[i] = mi;
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

template<typename FType, typename DType, typename IType>
//leNPknown<FType, DType, IType>::FinalizeInterv(vector<double>& miscore, vector<double>& chi2score, vector<double>& giniscore, DType& bTime, DType& sTime) {
void OnlineQuantileNPknown<FType, DType, IType>::FinalizeInterv(double* miscore, double* chi2score, double* giniscore, DType& bTime, DType& sTime, IType outnum, IType fnum) {
	int n = c1 + c0;
	int totalf = (int)sketch_collections.size();
	//chi2score.reserve(totalf);
	//giniscore.reserve(totalf);
	//miscore.reserve(totalf);
	//using LabelEntry = LabelEntry<float, double, int>;
	for (int i = 0; i < totalf; ++i) {
		startT = high_resolution_clock::now();
		NoneDriftQSketch::SummaryContainer out;
		std::unordered_map<int, std::vector<NoneDriftQSketch>>::iterator fi = sketch_collections.find(i);
		if (fi->second.size() == 1) {
			fi->second.front().GetSummary(&out, 1.0 / (_factor));
		}
		else {
			NoneDriftQSketch::SummaryContainer frontSummary, backSummary;
			if (fi->second.front().temp.data.size() == 0) {
				fi->second.front().GetSummary(&frontSummary, 1.0 / (_factor));
			}
			else {
				frontSummary = fi->second.front().temp;
			}
			fi->second.back().GetSummary(&backSummary, 1.0 / (_factor));
			NoneDriftQSketch union_sketch;
			union_sketch.temp.SetCombine(frontSummary, backSummary);
			out = union_sketch.temp;
		}
		//sketch_collections.erase(fi);
		vector<int> cl0(_numbin, 0), cl1(_numbin, 0);
		OnlineQuantileNPknown::GetBinVector(cl0, cl1, out, n);

		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//********end of sketch*************
		startT = high_resolution_clock::now();
		double chi2 = 0, gini = 0, mi = 0;
		OnlineQuantileNPknown::GetScore(chi2, gini, mi, cl0, cl1, c0, c1);

	/*	if (outnum * i + fnum - 1 < 0 || outnum * i + fnum - 1 > (1000 * 1000 - 1)) {
			int check = 1;
		}*/
		miscore[outnum * i + fnum - 1] = mi;
		chi2score[outnum * i + fnum - 1] = chi2;
		giniscore[outnum * i + fnum - 1] = gini;
	/*	chi2score.push_back(chi2);
		giniscore.push_back(gini);
		miscore.push_back(mi);*/
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

//======================drift none sparse=================================
template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknownDrift<FType, DType, IType>::stuffBatch(vector<double>& x, vector<double>& y, IType batchSize, double alpha, double beta) {
	batchend = batchSize;
	_x = x;
	_y = y;
	_alpha = alpha;
	_beta = beta;
}

template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknownDrift<FType, DType, IType>::BatchPenal(std::unordered_map<int, std::vector<DriftQSketch>>::iterator inputfi, double batchalpha) {
	for (int i = 0; i < inputfi->second.size(); i++) {
		if (!inputfi->second[i].temp.data.empty()) {
			for (std::vector<DriftQSketch::Entry>::iterator it = inputfi->second[i].temp.data.begin(); it != inputfi->second[i].temp.data.end(); ++it) {
				it->sweight0 *= batchalpha;
				it->sweight1 *= batchalpha;
			}
		}
		else {
			if (!inputfi->second[i].inqueue.queue.empty()) {
				for (std::vector<DriftQSketch::Summary::Queue::QEntry>::iterator it = inputfi->second[i].inqueue.queue.begin(); it != inputfi->second[i].inqueue.queue.end(); ++it) {
					it->weight0 *= batchalpha;
					it->weight1 *= batchalpha;
				}
			}
			if (inputfi->second[i].level.size() > 1) {
				for (std::vector<DriftQSketch::Summary>::iterator it = inputfi->second[i].level.begin() + 1; it != inputfi->second[i].level.end(); ++it) {
					if (!it->data.empty()) {
						for (std::vector<DriftQSketch::Entry>::iterator ik = it->data.begin(); ik != it->data.end(); ++ik) {
							ik->sweight0 *= batchalpha;
							ik->sweight1 *= batchalpha;
						}
					}
				}
			}
		}
	}
}

template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknownDrift<FType, DType, IType>::TrainSummary(double batchalpha) {
	startT = high_resolution_clock::now();

	for (int j = 0; j < _P; j++) {
		stream_start = backup_start;
		stream_seg = backup_seg;
		initSize = backup_initsize;
		stream_end = backup_end;
		startsummary = backup_startsumm;
		std::unordered_map<int, std::vector<DriftQSketch>>::iterator fi = sketch_collections.find(j);
		if (fi != sketch_collections.end() && batchalpha) {
			BatchPenal(fi, batchalpha);
			/*for (int i = 0; i < fi->second.size(); i++) {
				if (!fi->second[i].temp.data.empty()) {
					for (std::vector<DriftQSketch::Entry>::iterator it = fi->second[i].temp.data.begin(); it != fi->second[i].temp.data.end(); ++it) {
						it->sweight0 *= batchalpha;
						it->sweight1 *= batchalpha;
					}
				}
				else {
					if (!fi->second[i].inqueue.queue.empty()) {
						for (std::vector<DriftQSketch::Summary::Queue::QEntry>::iterator it = fi->second[i].inqueue.queue.begin(); it != fi->second[i].inqueue.queue.end(); ++it) {
							it->weight0 *= batchalpha;
							it->weight1 *= batchalpha;
						}
					}
					if (fi->second[i].level.size() > 1) {
						for (std::vector<DriftQSketch::Summary>::iterator it = fi->second[i].level.begin() + 1; it != fi->second[i].level.end(); ++it) {
							if (!it->data.empty()) {
								for (std::vector<DriftQSketch::Entry>::iterator ik = it->data.begin(); ik != it->data.end(); ++ik) {
									ik->sweight0 *= batchalpha;
									ik->sweight1 *= batchalpha;
								}
							}
						}
					}
				}
			}*/
		}
		for (int i = 0; i < batchend; i++) {
			int col = j;
			int addre = batchend * j + i;
			double v = _x[addre];//n*j+i
			int label = (int)_y[i];
			if (col == 0) {
				if (label == 1) {
					c1++;
				}
				else {
					c0++;
				}
			}
			
			if (fi == sketch_collections.end()) {
				DriftQSketch current_sketch;
				std::vector<DriftQSketch> sketchVector;
				current_sketch.Init(initSize, 1.0 / (_factor), _alpha, _beta);
				current_sketch.Push(label, v, _weight);
				sketchVector.push_back(current_sketch);
				sketch_collections.insert(std::unordered_map<int, std::vector<DriftQSketch>>::value_type(col, sketchVector));
				fi = sketch_collections.find(col);
			}
			else if (startsummary == 1) {
				if (stream_seg == 1) {
					DriftQSketch current_sketch;
					current_sketch.Init(initSize, 1.0 / (_factor), _alpha, _beta);
					current_sketch.Push(label, v, _weight);
					fi->second.push_back(current_sketch);
				}
				else {
					DriftQSketch union_sketch;
					GetSegSummary(union_sketch, &fi->second, stream_seg);
					//put into first
					fi->second.front() = union_sketch;
					//inital second to new
					fi->second.back().Init(initSize, 1.0 / (_factor), _alpha, _beta);
					fi->second.back().Push(label, v, _weight);
				}
				startsummary = 0;
			}
			else {
				fi->second.back().Push(label, v, _weight);
			}
			--stream_end;
			if (stream_end - stream_start + 1 == 0) {
				++stream_seg;
				stream_start = (int)(pow(2, stream_seg) - 1) * _factor;
				stream_end = (int)(pow(2, stream_seg + 1) - 1) * _factor - 1;
				initSize = (int)pow(2, stream_seg) * _factor;
				startsummary = 1;
			}
		}
		if (j == _P - 1) {
			backup_start = stream_start;
			backup_end = stream_end;
			backup_seg = stream_seg;
			backup_initsize = initSize;
			backup_startsumm = startsummary;
		}
	}//end of each feature
	stopT = high_resolution_clock::now();
	binTime += stopT - startT;
	//// ctime() used to give the present time 
	//printf("\ttime of TrainSummary: %f\n", (stopT - startT).count());
	//fflush(stdout);
}

template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknownDrift<FType, DType, IType>::GetSegSummary(DriftQSketch& segS, std::vector<DriftQSketch, std::allocator<DriftQSketch>>* sketch, int seg) {
	//combine last two summary
	DriftQSketch::SummaryContainer frontSummary, backSummary;
	if (sketch->front().temp.data.size() == 0) {
		sketch->front().GetSummary(&frontSummary, 1.0 / (_factor));
		sketch->back().GetSummary(&backSummary, 1.0 / (_factor));
	}
	else {
		frontSummary = sketch->front().temp;
		sketch->back().GetSummary(&backSummary, 1.0 / (_factor));
	}
	int laststream = (int)pow(2, seg - 1) * _factor;
	for (std::vector<DriftQSketch::Entry>::iterator it = frontSummary.data.begin(); it != frontSummary.data.end(); ++it) {
		it->sweight0 = exp(log(it->sweight0) + laststream * log(_alpha));
		it->sweight1 = exp(log(it->sweight1) + laststream * log(_alpha));
	}
	segS.temp.SetCombine(frontSummary, backSummary);
}

template<typename FType, typename DType, typename IType>
template<typename Vtype>
void OnlineQuantileNPknownDrift<FType, DType, IType>::GetBinVector(Vtype& cl0, Vtype& cl1, DriftQSketch::SummaryContainer& insummary, int n) {
	double epsilonN = (double)1.0 / (_factor)*n;
	double est_bin_size = (double)n / _numbin;
	int current_bin = 0;
	double lastboundry = 0, boundry;
	int ispass = 0;
	LabelEntry lastentry = LabelEntry(0, 0, 0, 0, 0);
	float aprev_rmin = 0, bprev_rmin = 0;

	float x1 = 0, x0 = 0;
	for (auto& s : insummary.data) {
		x0 += lastentry.w0;
		x1 += lastentry.w1;
		cl0[current_bin] += lastentry.w0;
		cl1[current_bin] += lastentry.w1;
		if (ispass == 1) {
			if (s.value != lastentry.value) {
				boundry = round((current_bin + 1) * est_bin_size);
				boundry = (s.rmin - boundry) > (boundry - lastentry.rmax) ? (lastentry.rmax) : (s.rmin);
				lastboundry = boundry;
				while (boundry - round((current_bin + 1) * est_bin_size) >= 0) {
					++current_bin;
				}
				ispass = 0;
			}
		}
		else if (s.rmin >= round((current_bin + 1) * est_bin_size)) {// || lastentry.rmax >= (current_bin + 1)*est_bin_size) {
			if (s.value != lastentry.value) {
				boundry = round((current_bin + 1) * est_bin_size);
				boundry = (s.rmin - boundry) > (boundry - lastentry.rmax) ? lastentry.rmax : s.rmin;//(s.rmin + lastentry.rmax) / 2;					
				lastboundry = boundry;
				while (boundry - round((current_bin + 1) * est_bin_size) >= 0) {
					++current_bin;
				}
			}
			else ispass = 1;
		}

		lastentry = LabelEntry(s.rmin, s.rmax, s.sweight0, s.sweight1, s.value);
	}
	cl0[current_bin] += lastentry.w0;
	cl1[current_bin] += lastentry.w1;
}

template<typename FType, typename DType, typename IType>
template<typename Vtype>
void OnlineQuantileNPknownDrift<FType, DType, IType>::GetScore(double& chi2, double& gini, double& mi, Vtype& cl0, Vtype& cl1) {
	double totalW0 = std::accumulate(cl0.begin(), cl0.end(), 0.0);
	double totalW1 = std::accumulate(cl1.begin(), cl1.end(), 0.0), totalW = totalW0 + totalW1;
	//chi2
	double nlc, nlc0, nlc1;
	double nlc_hat1, nlc_hat0, part0, part1;

	for (int j = 0; j < _numbin; j++) {
		nlc1 = cl1[j];// (*cl1)[j];
		nlc0 = cl0[j];// (*cl0)[j];
		nlc = nlc1 + nlc0;
		nlc_hat0 = totalW0 * nlc / (double)totalW;
		nlc_hat1 = totalW1 * nlc / (double)totalW;
		if (nlc_hat0 == 0) part0 = 0; else part0 = (nlc0 - nlc_hat0) * (nlc0 - nlc_hat0) / nlc_hat0;
		if (nlc_hat1 == 0) part1 = 0; else part1 = (nlc1 - nlc_hat1) * (nlc1 - nlc_hat1) / nlc_hat1;
		chi2 += part0 + part1;
	}

	//Gini
	double ah = 0, bh = totalW, ah0 = 0, ah1 = 0, bh0 = totalW0, bh1 = totalW1;
	double  pah, pbh, pah0, pah1, pbh0, pbh1, parta, partb;
	vector<double> gini_column;
	for (int j = 0; j < _numbin; j++) {
		if (ah == 0) parta = 0; else {
			pah = ah / (double)totalW;
			pah0 = ah0 / (double)ah;
			pah1 = ah1 / (double)ah;
			parta = pah * (1 - pow(pah0, 2) - pow(pah1, 2));
		}
		if (bh == 0) partb = 0; else {
			pbh = bh / (double)totalW;
			pbh0 = bh0 / (double)bh;
			pbh1 = bh1 / (double)bh;
			partb = pbh * (1 - pow(pbh0, 2) - pow(pbh1, 2));
		}
		gini_column.push_back(parta + partb);

		ah0 += cl0[j];// (*cl0)[j];
		ah1 += cl1[j];// (*cl1)[j];
		ah = ah0 + ah1;

		bh0 -= cl0[j];// (*cl0)[j];
		bh1 -= cl1[j];// (*cl1)[j];
		bh = bh1 + bh0;
	}
	gini = *std::min_element(gini_column.begin(), gini_column.end());

	//MI
	double px, py0 = totalW0 / (double)totalW, py1 = totalW1 / (double)totalW, pxy1, pxy0;

	for (int j = 0; j < _numbin; j++) {
		nlc1 = cl1[j];// (*cl1)[j];
		nlc0 = cl0[j];// (*cl0)[j];
		nlc = nlc1 + nlc0;
		px = nlc / (double)totalW;
		pxy0 = nlc0 / (double)totalW;
		pxy1 = nlc1 / (double)totalW;
		if (pxy0 == 0) part0 = 0; else part0 = pxy0 * log(pxy0 / (px * py0));
		if (pxy1 == 0) part1 = 0; else part1 = pxy1 * log(pxy1 / (px * py1));
		mi += part0 + part1;
	}
}

template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknownDrift<FType, DType, IType>::Finalize(double* binMatrix, double* miscore, double* chi2score, double* giniscore, DType& bTime, DType& sTime) {
	int n = c1 + c0;
	int totalf = (int)sketch_collections.size();
	//using LabelEntry = LabelEntry<float, double, int>;
	for (int i = 0; i < totalf; ++i) {
		startT = high_resolution_clock::now();
		DriftQSketch::SummaryContainer out;
		std::unordered_map<int, std::vector<DriftQSketch>>::iterator fi = sketch_collections.find(i);
		if (fi->second.size() == 1) {
			fi->second.front().GetSummary(&out, 1.0 / (_factor));
		}
		else {
			DriftQSketch::SummaryContainer frontSummary, backSummary;
			if (fi->second.front().temp.data.size() == 0) {
				fi->second.front().GetSummary(&frontSummary, 1.0 / (_factor));
			}
			else {
				frontSummary = fi->second.front().temp;
			}
			int laststream = initSize - (stream_end - stream_start + 1);
			for (std::vector<DriftQSketch::Entry>::iterator it = frontSummary.data.begin(); it != frontSummary.data.end(); ++it) {
				it->sweight0 = exp(log(it->sweight0) + laststream * log(_alpha));
				it->sweight1 = exp(log(it->sweight1) + laststream * log(_alpha));
			}
			fi->second.back().GetSummary(&backSummary, 1.0 / (_factor));
			DriftQSketch union_sketch;
			union_sketch.temp.SetCombine(frontSummary, backSummary);
			out = union_sketch.temp;
		}
		sketch_collections.erase(fi);
		vector<float> cl0(_numbin, 0), cl1(_numbin, 0);
		GetBinVector(cl0, cl1, out, n);

		for (int b = 0; b < _numbin; ++b) {
			binMatrix[_numbin * 2 * i + b] = cl0[b];
			binMatrix[_numbin * 2 * i + b + _numbin] = cl1[b];
		}
		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//********end of sketch*************
		startT = high_resolution_clock::now();
		double chi2 = 0, gini = 0, mi = 0;
		GetScore(chi2, gini, mi, cl0, cl1);

		chi2score[i] = chi2;
		giniscore[i] = gini;
		miscore[i] = mi;
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

template<typename FType, typename DType, typename IType>
void OnlineQuantileNPknownDrift<FType, DType, IType>::FinalizeInterv(vector<double>& miscore, vector<double>& chi2score, vector<double>& giniscore, DType& bTime, DType& sTime) {
	int n = c1 + c0;
	int totalf = (int)sketch_collections.size();
	//using LabelEntry = LabelEntry<float, double, int>;
	for (int i = 0; i < totalf; ++i) {
		startT = high_resolution_clock::now();
		DriftQSketch::SummaryContainer out;
		std::unordered_map<int, std::vector<DriftQSketch>>::iterator fi = sketch_collections.find(i);
		std::vector<DriftQSketch> summaryTemp = fi->second;
		if (summaryTemp.size() == 1) {
			summaryTemp.front().GetSummary(&out, 1.0 / (_factor));
		}
		else {
			DriftQSketch::SummaryContainer frontSummary, backSummary;
			if (summaryTemp.front().temp.data.size() == 0) {
				summaryTemp.front().GetSummary(&frontSummary, 1.0 / (_factor));
			}
			else {
				frontSummary = summaryTemp.front().temp;
			}
			int laststream = initSize - (stream_end - stream_start + 1);
			for (std::vector<DriftQSketch::Entry>::iterator it = frontSummary.data.begin(); it != frontSummary.data.end(); ++it) {
				it->sweight0 = exp(log(it->sweight0) + laststream * log(_alpha));
				it->sweight1 = exp(log(it->sweight1) + laststream * log(_alpha));
			}
			summaryTemp.back().GetSummary(&backSummary, 1.0 / (_factor));
			DriftQSketch union_sketch;
			union_sketch.temp.SetCombine(frontSummary, backSummary);
			out = union_sketch.temp;
		}
		//sketch_collections.erase(fi);
		vector<float> cl0(_numbin, 0), cl1(_numbin, 0);
		GetBinVector(cl0, cl1, out, n);

		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//********end of sketch*************
		startT = high_resolution_clock::now();
		double chi2 = 0, gini = 0, mi = 0;
		GetScore(chi2, gini, mi, cl0, cl1);

		chi2score.push_back(chi2);
		giniscore.push_back(gini);
		miscore.push_back(mi);
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

//=========================sparse=======================================================
template<typename FType, typename DType, typename IType, typename CType>
void OnlineQuantileNPunknown<FType, DType, IType, CType>::InitFiles(CType* path, CType* prefix, CType* extension, IType totalfiles) {
	_path = path;
	_prefix = prefix;
	_extension = extension;
	_totalfiles = totalfiles;
}

template<typename FType, typename DType, typename IType, typename CType>
int OnlineQuantileNPunknown<FType, DType, IType, CType>::TrainSummary() {

	for (int d = 0; d < _totalfiles; d++)
	{
		//printf("file %d\n", d);
		PySys_WriteStdout("file %d\n", d);
		PyRun_SimpleString("import sys; sys.stdout.flush()");
		/*printf("varsize %d\n", vars.size());
		fflush(stdout);*/
		PySys_WriteStdout("\tvarsize %d\n", vars.size());
		PyRun_SimpleString("import sys; sys.stdout.flush()");
		sprintf(name, "%s/%s%d.%s", _path, _prefix, d, _extension);
		vector<vector<std::pair<int, float>>> x;
		vector<float> y;

		if (!ReadSvm(x, y, name, " ")) {
			//mexErrMsgTxt("File not found.");
			PyErr_SetString(PyExc_FileNotFoundError, "File not found.");
			return NULL;  // Critical: Return NULL to propagate the error
		}
		/*total row number for silumating row input using for loop*/
		int nr = (int)x.size();
		/* = simulate input one row at a time*/
		startT = high_resolution_clock::now();
		for (int i = 0; i < nr; i++)
		{
			int label = (int)y[i];
			int labelwhere = (int)(label == 1);
			if (label == 1)
				c1++;
			else
				c0++;
			for (int j = 0; j < x[i].size(); j++) {
				int idx = x[i][j].first;
				double v = x[i][j].second;

				vars.insert(idx);

				std::unordered_map<int, std::pair<std::pair<std::vector<int>, std::vector<int>>, std::vector<NoneDriftQSketch>>>::iterator fi = sketch_collections.find(idx);
				if (fi == sketch_collections.end()) {
					NoneDriftQSketch current_sketch;
					/*= <label count, subsegment, substream size, substream start point, substream end point, if start new summary><vector of two summary>*/
					std::pair<std::pair<std::vector<int>, std::vector<int>>, std::vector<NoneDriftQSketch>> sketchVector;
					sketchVector.first.first.push_back(0);//label count
					sketchVector.first.first.push_back(0);
					sketchVector.first.first[labelwhere] += 1;
					sketchVector.first.second.push_back(0);//subsegment
					sketchVector.first.second.push_back((int)pow(2, sketchVector.first.second[0]) * _factor);//substream size
					sketchVector.first.second.push_back((int)(pow(2, sketchVector.first.second[0]) - 1) * _factor);//substream start point
					sketchVector.first.second.push_back((int)(pow(2, sketchVector.first.second[0] + 1) - 1) * _factor - 1);//substream end point
					sketchVector.first.second.push_back(0);//if start new summary
					current_sketch.Init(sketchVector.first.second[1], 1.0 / (_factor));
					current_sketch.Push(label, v, _weight);
					sketchVector.second.push_back(current_sketch);
					sketch_collections.insert(std::unordered_map<int, std::pair<std::pair<std::vector<int>, std::vector<int>>, std::vector<NoneDriftQSketch>>>::value_type(idx, sketchVector));
					fi = sketch_collections.find(idx);
				}
				else if (fi->second.first.second.back() == 1) {
					fi->second.first.first[labelwhere] += 1;
					if (fi->second.first.second[0] == 1) {
						NoneDriftQSketch current_sketch;
						current_sketch.Init(fi->second.first.second[1], 1.0 / (_factor));
						current_sketch.Push(label, v, _weight);
						fi->second.second.push_back(current_sketch);
					}
					else {
						//combine last two summary						
						//NoneDriftQSketch::SummaryContainer frontSummary, backSummary;
						//if (fi->second.first.second[0] == 2) {
						//	fi->second.second.front().GetSummary(&frontSummary, 1.0 / (_factor));
						//	fi->second.second.back().GetSummary(&backSummary, 1.0 / (_factor));
						//}
						//else {
						//	frontSummary = fi->second.second.front().temp;
						//	fi->second.second.back().GetSummary(&backSummary, 1.0 / (_factor));
						//}
						NoneDriftQSketch union_sketch;
						OnlineQuantileNPknown<FType, DType, IType>::GetSegSummary(union_sketch, &fi->second.second);
						//union_sketch.temp.SetCombine(frontSummary, backSummary);
						//put into first
						fi->second.second.front() = union_sketch;
						//inital second to new
						fi->second.second.back().Init(fi->second.first.second[1], 1.0 / (_factor));
						fi->second.second.back().Push(label, v, _weight);
					}
					//fi->second.front().temp.data = &fi->second.front().temp.data[0];//adjust pointer to right position
					fi->second.first.second.back() = 0;
				}
				else {
					fi->second.first.first[labelwhere] += 1;
					fi->second.second.back().Push(label, v, _weight);
				}
				fi->second.first.second[3] -= 1;
				if (fi->second.first.second[3] - fi->second.first.second[2] + 1 == 0) {
					fi->second.first.second[0] += 1;
					fi->second.first.second[2] = (pow(2, fi->second.first.second[0]) - 1) * _factor;
					fi->second.first.second[3] = (pow(2, fi->second.first.second[0] + 1) - 1) * _factor - 1;
					fi->second.first.second[1] = pow(2, fi->second.first.second[0]) * _factor;
					fi->second.first.second.back() = 1;
				}
			}
		}
		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//end of file
	}
	return (int)vars.size();
}

template<typename FType, typename DType, typename IType, typename CType>
void OnlineQuantileNPunknown<FType, DType, IType, CType>::Finalize(double* binMatrix, double* miscore, double* chi2score, double* giniscore, std::set<int>& varout, DType& bTime, DType& sTime) {
	double n = c1 + c0;
	int si = 0;
	for (std::set<int>::iterator vi = vars.begin(); vi != vars.end(); ++vi) {
		startT = high_resolution_clock::now();
		NoneDriftQSketch::SummaryContainer out;
		std::unordered_map<int, std::pair<std::pair<std::vector<int>, std::vector<int>>, std::vector<NoneDriftQSketch>>>::iterator fi = sketch_collections.find(*vi);


		if (fi->second.second.size() == 1) {
			fi->second.second.front().Push(1, 0, c1 - fi->second.first.first[1]);
			fi->second.second.front().Push(-1, 0, c0 - fi->second.first.first[0]);
			fi->second.second.front().GetSummary(&out, 1.0 / (_factor));
		}
		else {
			fi->second.second.back().Push(1, 0, c1 - fi->second.first.first[1]);
			fi->second.second.back().Push(-1, 0, c0 - fi->second.first.first[0]);
			NoneDriftQSketch::SummaryContainer frontSummary, backSummary;
			if (fi->second.second.front().temp.data.size() == 0) {
				fi->second.second.front().GetSummary(&frontSummary, 1.0 / (_factor));
			}
			else {
				frontSummary = fi->second.second.front().temp;
			}
			fi->second.second.back().GetSummary(&backSummary, 1.0 / (_factor));
			NoneDriftQSketch union_sketch;
			union_sketch.temp.SetCombine(frontSummary, backSummary);
			out = union_sketch.temp;
		}
		sketch_collections.erase(fi);
		vector<int> cl0(_numbin, 0), cl1(_numbin, 0);
		OnlineQuantileNPknown<FType, DType, IType>::GetBinVector(cl0, cl1, out, n);

		for (int b = 0; b < _numbin; ++b) {
			binMatrix[_numbin * 2 * si + b] = cl0[b];
			binMatrix[_numbin * 2 * si + b + _numbin] = cl1[b];
		}
		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//********end of sketch*************
		startT = high_resolution_clock::now();
		double chi2 = 0, gini = 0, mi = 0;
		OnlineQuantileNPknown<FType, DType, IType>::GetScore(chi2, gini, mi, cl0, cl1, c0, c1);

		chi2score[si] = chi2;
		giniscore[si] = gini;
		miscore[si] = mi;
		stopT = high_resolution_clock::now();
		scoreTime += stopT - startT;

		si++;
	}
	bTime = binTime.count();
	sTime = scoreTime.count();
	varout = vars;
}

//=====================drift sparse=======================================================
template<typename FType, typename DType, typename IType, typename CType>
void OnlineQuantileNPunknownDrift<FType, DType, IType, CType>::InitFiles(CType* path, CType* prefix, CType* extension, IType totalfiles, double alpha, double beta) {
	_path = path;
	_prefix = prefix;
	_extension = extension;
	_totalfiles = totalfiles;
	_alpha = alpha;
	_beta = beta;
	penaltimes = 0; d = 0; nrows = 0;
}

template<typename FType, typename DType, typename IType, typename CType>
void OnlineQuantileNPunknownDrift<FType, DType, IType, CType>::BatchPenal(std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>>::iterator inputfi, double batchalpha) {
	for (int i = 0; i < inputfi->second.second.size(); i++) {
		if (!inputfi->second.second[i].temp.data.empty()) {
			for (std::vector<DriftQSketch::Entry>::iterator it = inputfi->second.second[i].temp.data.begin(); it != inputfi->second.second[i].temp.data.end(); ++it) {
				it->sweight0 *= batchalpha;
				it->sweight1 *= batchalpha;
			}
		}
		else {
			if (!inputfi->second.second[i].inqueue.queue.empty()) {
				for (std::vector<DriftQSketch::Summary::Queue::QEntry>::iterator it = inputfi->second.second[i].inqueue.queue.begin(); it != inputfi->second.second[i].inqueue.queue.end(); ++it) {
					it->weight0 *= batchalpha;
					it->weight1 *= batchalpha;
				}
			}
			if (inputfi->second.second[i].level.size() > 1) {
				for (std::vector<DriftQSketch::Summary>::iterator it = inputfi->second.second[i].level.begin() + 1; it != inputfi->second.second[i].level.end(); ++it) {
					if (!it->data.empty()) {
						for (std::vector<DriftQSketch::Entry>::iterator ik = it->data.begin(); ik != it->data.end(); ++ik) {
							ik->sweight0 *= batchalpha;
							ik->sweight1 *= batchalpha;
						}
					}
				}
			}
		}
	}
}

template<typename FType, typename DType, typename IType, typename CType>
int OnlineQuantileNPunknownDrift<FType, DType, IType, CType>::TrainSummary(double batchalpha) {

	for (d = 0; d < _totalfiles; d++){
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
		//vector<vector<std::pair<int, float>>> x;
		//vector<float> y;
		//debug1 = high_resolution_clock::now();
		////if (!ReadSvm(x, y, name, " "))
		////	mexErrMsgTxt("File not found.");
		//debug2 = high_resolution_clock::now();
		//debug3 = debug2 - debug1;
		//printf("\ttime of read data: %f\n", debug3.count());
		/*total row number for silumating row input using for loop*/
		int adjustcount;//nr = (int)x.size(),

		/* = simulate input one row at a time*/
		/*char* tmp, * p, * tok;*/
		//vstrings.clear();

		//if (str == NULL) return;

		/*tmp = new char[strlen(str) + 1];
		strcpy(tmp, str);*/

		//for (p = tmp; tok = strtok(p, dlm); p = NULL)
		//	//		if (strlen(tok)>0)
		//	vstrings.push_back(tok);

		//delete[] tmp;
		char line[100000];
		//std::vector<std::string> v, v2;
		FILE* f = fopen(name, "rt");
		if (f == 0)
			return false;
		int numf = 0;
		nrows = 0;
		while (!feof(f)) {
			//std::vector<std::pair<int, Tp>> tmp;
			//tmp.reserve(1000);
			//char *tmp, *p, *tok;
			nrows++;
			int head = 1, label;
			if (fgets(line, 100000, f) == 0)
				break;
			/*const char *str = line, *dlm = &' ';
			tmp = new char[strlen(line) + 1];
			strcpy(tmp, str);*/
			char* end_str;
			char* token = strtok_s(line, " ", &end_str);
			while (token != NULL) {
				//for (p = tmp; tok = strtok(p, dlm); p = NULL){
						//		if (strlen(tok)>0)
						//vstrings.push_back(tok);

						//delete[] tmp;
					/*		for (int i = 1; i < (int)v.size(); i++) {
								int idx = atoi(v2[0].c_str());
								Tp val = (Tp)atof(v2[1].c_str());
								tmp.push_back(std::pair<int, Tp>(idx, val));
							}
							y.push_back((TpY)atof(v[0].c_str()));
							x.push_back(tmp);
						}*/
				debug4 = high_resolution_clock::now();
				startT = high_resolution_clock::now();
				/*for (int i = 0; i < nr; i++)
				{*/

				if (head == 1) {
					label = std::stoi(token);
					Yid.push_back(label);
					if (label == 1)
						c1++;
					else
						c0++;
					head = 0;
				}
				else {
					//char *tmp1;
					//const char* dlm = &':';
					//tmp1 = new char[strlen(tok.c_str()) + 1];
					//strcpy(tmp1, tok);
					if (nrows > 15000) numf++;
					char* end_token;
					char* smalltoken = strtok_s(token, ":", &end_token);
					int idx = std::stoi(smalltoken);
					smalltoken = strtok_s(NULL, ":", &end_token);
					double v = (double)std::stof(smalltoken);
					//for (p = tmp; tok = strtok(p, ':'); p = NULL)
					//	//		if (strlen(tok)>0)
					//	vstrings.push_back(tok);


					//int label = (int)y[i];
					//int labelwhere = (int)(label == 1);


					//for (int j = 0; j < x[i].size(); j++) {
					//	int idx = x[i][j].first;
					//	////debug
					//if (idx != 471) {//debug
					//	token = strtok_s(NULL, " ", &end_str);
					//	continue;
					//}
					//	double v = x[i][j].second;

					vars.insert(idx);
				/* 	if (c0 + c1 == 1500) {
						int check = 1;
					} */
					//if (idx == 2) {
						//int check = 1;
					/*if (c0 + c1 == 10499) {
						int check = 1;
					}*/

					std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>>::iterator fi = sketch_collections.find(idx);
					if (fi == sketch_collections.end()) {
						
						DriftQSketch current_sketch;
						/*= <label count, subsegment, substream size, substream start point, substream end point, if start new summary><vector of two summary>*/
						std::pair<std::vector<int>, std::vector<DriftQSketch>> sketchVector;
						//std::pair<std::pair<std::vector<float>, std::vector<int>>, std::vector<DriftQSketch>> sketchVector;
						//sketchVector.first.first.push_back(0.0);//record _weight of 0 value for label 0
						//sketchVector.first.first.push_back(0.0);//record _weight of 0 value for label 1
						//sketchVector.first.first[labelwhere] = _rateI / (_rateI - 1);
						sketchVector.first.push_back(0);//subsegment
						sketchVector.first.push_back(c0);//number of instances until last none 0 value for label 0
						sketchVector.first.push_back(c1);//number of instances until last none 0 value for label 1
						sketchVector.first.push_back(0);//substream's previous adjusted startpoint
						sketchVector.first.push_back((int)pow(2, sketchVector.first[0]) * _factor);//substream size
						sketchVector.first.push_back((int)(pow(2, sketchVector.first[0]) - 1) * _factor);//substream start point
						sketchVector.first.push_back((int)(pow(2, sketchVector.first[0] + 1) - 1) * _factor - 1);//substream end point
						sketchVector.first.push_back(0);//if start new summary
						sketchVector.first.push_back(0);//penalty performed
						current_sketch.Init(sketchVector.first[4], 1.0 / (_factor), _alpha, _beta);
						if (c0 + c1 == 1) {
							current_sketch.PushSparse(label, v, coverage, (double)_weight, 0);
							adjustcount = 1;
						}
						else {
							double firstw0, firstw1;
							if (d != 0 && nrows == 1 && batchalpha) {
								firstw0 = generalweight[0] * batchalpha; firstw1 = generalweight[1] * batchalpha;
								sketchVector.first.back() += 1;
							}
							else {
								firstw0 = generalweight[0]; firstw1 = generalweight[1];
							}
							if (label == 1) {
								current_sketch.PushSparse(0, 0, c0 * coverage, firstw0, 0);
								current_sketch.PushSparse(1, 0, (c1 - 1) * coverage, firstw1, 1);
							}
							else {
								current_sketch.PushSparse(0, 0, (c0 - 1) * coverage, firstw0, 0);
								current_sketch.PushSparse(1, 0, c1 * coverage, firstw1, 1);
							}
							current_sketch.PushSparse(label, v, coverage, (double)_weight, 0);
							adjustcount = c0 + c1;//log: remove "+ 1"
							//adjustcount = 2;
						}
						sketchVector.second.push_back(current_sketch);
						sketch_collections.insert(std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>>::value_type(idx, sketchVector));
						fi = sketch_collections.find(idx);
					}
					else if (fi->second.first[7] == 1) {
						//what's last record?????????
						//if (idx == 471) {//debug
						//	int check = 1;
						//}
				/*		int lastrecord0 = fi->second.first.second[1];
						int lastrecord1 = fi->second.first.second[2];*/
						if (fi->second.second.size() == 1) {
							DriftQSketch current_sketch;
							fi->second.second.push_back(current_sketch);
							//fi->second.second.back().Init(initSize, 1.0 / (_factor),  _alpha, _beta);
							fi->second.second.back().Init(fi->second.first[4], 1.0 / (_factor), _alpha, _beta);
							ChoisePush(fi, adjustcount, label, v, batchalpha);
							/*current_sketch.Init(fi->second.first.second[3], 1.0 / (_factor), _rateI);
							if (c0 + c1 - lastrecord0 - lastrecord1 - 1 == 0) {
								current_sketch.PushSparse(label, v, coverage, (float)_weight);
								adjustcount = 1;
							}
							else {
								if (label == 1) {
									current_sketch.PushSparse(0, 0, (c0 - lastrecord) * coverage, fi->second.first.first[0]);
									current_sketch.PushSparse(1, 0, (c1 - lastrecord - 1) * coverage, fi->second.first.first[1]);
								}
								else {
									current_sketch.PushSparse(0, 0, (c0 - lastrecord - 1) * coverage, fi->second.first.first[0]);
									current_sketch.PushSparse(1, 0, (c1 - lastrecord) * coverage, fi->second.first.first[1]);
								}
								current_sketch.PushSparse(label, v, coverage, (float)_weight);
								adjustcount = c0 + c1 - lastrecord0 - lastrecord1;
							}
							fi->second.second.push_back(current_sketch);*/
						}
						else {
							//combine last two summary						
							DriftQSketch union_sketch;
							//using stream begin - dataset begin as power value of front summary
							GetSegSummary(union_sketch, fi->second);
							//union_sketch.temp.SetCombine(frontSummary, backSummary);
							//put into first
							fi->second.second.front() = union_sketch;
							//inital second to new
							fi->second.second.back().Init(fi->second.first[4], 1.0 / (_factor), _alpha, _beta);
							//if (c0 + c1 - lastrecord0 - lastrecord1 - 1 == 0) {
							//	fi->second.second.back().PushSparse(label, v, coverage, (float)_weight);
							//	adjustcount = 1;
							//}
							//else {
							//	if (label == 1) {
							//		fi->second.second.back().PushSparse(0, 0, (c0 - lastrecord) * coverage, fi->second.first.first[0]);
							//		fi->second.second.back().PushSparse(1, 0, (c1 - lastrecord - 1) * coverage, fi->second.first.first[1]);
							//	}
							//	else {
							//		fi->second.second.back().PushSparse(0, 0, (c0 - lastrecord - 1) * coverage, fi->second.first.first[0]);
							//		fi->second.second.back().PushSparse(1, 0, (c1 - lastrecord) * coverage, fi->second.first.first[1]);
							//	}
							//	fi->second.second.back().PushSparse(label, v, coverage, (float)_weight);
							//	adjustcount = c0 + c1 - lastrecord0 - lastrecord1;
							//}
							ChoisePush(fi, adjustcount, label, v, batchalpha);
						}
						//fi->second.front().temp.data = &fi->second.front().temp.data[0];//adjust pointer to right position
						fi->second.first[7] = 0;
						//fi->second.first.first = c0 + c1;
						/*fi->second.first.first[labelwhere] = _rateI / (_rateI - 1);
						fi->second.first.first[1-labelwhere] = 0.0;*/
						fi->second.first[1] = c0;
						fi->second.first[2] = c1;
					}
					else {
						//what's last record?????????
						/*int lastrecord0 = fi->second.first.second[1];
						int lastrecord1 = fi->second.first.second[2];*/
						//if (c0 + c1 - lastrecord0 - lastrecord1 - 1 == 0) {
						//	fi->second.second.back().PushSparse(label, v, coverage, (float)_weight);
						//	adjustcount = 1;
						//}
						//else {
						//	if (label == 1) {
						//		fi->second.second.back().PushSparse(0, 0, (c0 - lastrecord) * coverage, fi->second.first.first[0]);
						//		fi->second.second.back().PushSparse(1, 0, (c1 - lastrecord - 1) * coverage, fi->second.first.first[1]);
						//	}
						//	else {
						//		fi->second.second.back().PushSparse(0, 0, (c0 - lastrecord - 1) * coverage, fi->second.first.first[0]);
						//		fi->second.second.back().PushSparse(1, 0, (c1 - lastrecord) * coverage, fi->second.first.first[1]);
						//	}
						//	fi->second.second.back().PushSparse(label, v, coverage, (float)_weight);
						//	adjustcount = c0 + c1 - lastrecord0 - lastrecord1;
						//}
						ChoisePush(fi, adjustcount, label, v, batchalpha);
						//fi->second.first.first = c0 + c1;
						/*fi->second.first.first[labelwhere] = _rateI / (_rateI - 1);
						fi->second.first.first[1 - labelwhere] = 0.0;*/
						fi->second.first[1] = c0;
						fi->second.first[2] = c1;
					}
					
					fi->second.first[6] -= adjustcount;
					/*if (fi->second.first[6] - fi->second.first[5] + 1 < 0) {
						int check = 1;
					}*/
					if (fi->second.first[6] - fi->second.first[5] + 1 <= 0) {
						fi->second.first[0] += 1;
						fi->second.first[3] = fi->second.first[5];
						//fi->second.first[3] = fi->second.first[5]- fi->second.first[3];//substream's previous adjusted startpoint
						//2*fi->second.first.second[5]+fi->second.first.second[4]-fi->second.first.second[6]  - 1;
						fi->second.first[5] = 2 * fi->second.first[5] + fi->second.first[4] - fi->second.first[6] - 1;//substream start point
						fi->second.first[4] = pow(2, fi->second.first[0]) * _factor;//substream size
						fi->second.first[6] = fi->second.first[5] + fi->second.first[4] - 1;//substream end point
						fi->second.first[7] = 1;
					}
					/*else if (fi->second.first.second[4] - fi->second.first.second[3] + 1 < 0) {

						fi->second.first.second[1] = fi->second.first.second[3];
						fi->second.first.second.back() = 1;
					}*/
					//}
				}
				token = strtok_s(NULL, " ", &end_str);
				debug5 = high_resolution_clock::now();
				debug6 += debug5 - debug4;
				//for not mentioned features
				//std::unordered_map<int, std::pair<std::pair<std::vector<float>, std::vector<int>>, std::vector<DriftQSketch>>>::iterator fi;
			}
			delete[] token;

			debug7 = high_resolution_clock::now();
			if (d != 0 && nrows == 1 && batchalpha) {
				penaltimes++;
				generalweight[1] = batchalpha * generalweight[1];
				generalweight[0] = batchalpha * generalweight[0];
			}
			if (label == 1) {
				//c1++; 
				/*for (fi = sketch_collections.begin(); fi != sketch_collections.end(); ++fi) {
					fi->second.first.first[1] = (1 - _rateI) * fi->second.first.first[1] + _rateI * 1;
					fi->second.first.first[0] = (1 - _rateI) * fi->second.first.first[0];
				}*/
				wtower1.push_back(_alpha* generalweight[1] + _beta * 1);
				wtower0.push_back(_alpha* generalweight[0]);
				generalweight[1] = _alpha * generalweight[1] + _beta * 1;
				generalweight[0] = _alpha * generalweight[0];
			}
			else {
				//c0++;
				/*for (fi = sketch_collections.begin(); fi != sketch_collections.end(); ++fi) {
					fi->second.first.first[0] = (1 - _rateI) * fi->second.first.first[0] + _rateI * 1;
					fi->second.first.first[1] = (1 - _rateI) * fi->second.first.first[1];
				}*/
				wtower0.push_back(_alpha* generalweight[0] + _beta * 1);
				wtower1.push_back(_alpha* generalweight[1]);
				generalweight[0] = _alpha * generalweight[0] + _beta * 1;
				generalweight[1] = _alpha * generalweight[1];
			}
			debug8 = high_resolution_clock::now();
			debug9 += debug8 - debug7;
		}
		/*printf("\tfeatures: %d\n", numf);
		fflush(stdout);*/
		PySys_WriteStdout("\tfeatures: %d\n", numf);
		PyRun_SimpleString("import sys; sys.stdout.flush()");
		fclose(f);
		//--stream_end;
		//if (stream_end - stream_start + 1 == 0) {
		//	for (fi = sketch_collections.begin(); fi != sketch_collections.end(); ++fi) {
		//		fi->second.first.second.back() = 1;
		//		int lastrecord0 = fi->second.first.second[1];
		//		int lastrecord1 = fi->second.first.second[2];
		//		if (c0 + c1 - lastrecord0 - lastrecord1 != 0) {
		//			fi->second.second.back().PushSparse(0, 0, (c0 - lastrecord0) * coverage, fi->second.first.first[0]);
		//			fi->second.second.back().PushSparse(1, 0, (c1 - lastrecord1) * coverage, fi->second.first.first[1]);
		//			//update
		//			fi->second.first.second[1] = c0;
		//			fi->second.first.second[2] = c1;
		//			fi->second.first.first[labelwhere] = 0.0;
		//			fi->second.first.first[1 - labelwhere] = 0.0;
		//		}
		//	}
		//	++stream_seg; 
		//	stream_start = (int)(pow(2, stream_seg) - 1) * _factor;
		//	stream_end = (int)(pow(2, stream_seg + 1) - 1) * _factor - 1;
		//	initSize = (int)pow(2, stream_seg) * _factor;
		//	//startsummary = 1;
		//}

		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		/*printf("\ttime of train current file: %f\n", debug6.count());
		fflush(stdout);
		printf("\ttime of fill empty feature: %f\n", debug9.count());
		fflush(stdout);*/
		//end of file
	}
	return (int)vars.size();
}

template<typename FType, typename DType, typename IType, typename CType>
void OnlineQuantileNPunknownDrift<FType, DType, IType, CType>::GetSegSummary(DriftQSketch& segS, std::pair<std::vector<int>, std::vector<DriftQSketch>>& context) {
	//combine last two summary
	DriftQSketch::SummaryContainer frontSummary, backSummary;
	if (context.second.front().temp.data.size() == 0) {
		context.second.front().GetSummary(&frontSummary, 1.0 / (_factor));
	}
	else {
		frontSummary = context.second.front().temp;
	}
	context.second.back().GetSummary(&backSummary, 1.0 / (_factor));
	int laststream = (int)(context.first[5] - context.first[3]);
	//int laststream = (int)context.first[3];
	for (std::vector<DriftQSketch::Entry>::iterator it = frontSummary.data.begin(); it != frontSummary.data.end(); ++it) {
		//it->sweight0 = exp(log(it->sweight0) + laststream * log(1 - _rateI));
		//it->sweight1 = exp(log(it->sweight1) + laststream * log(1 - _rateI));
		it->sweight0 = exp(log(it->sweight0) + laststream * log(_alpha));
		it->sweight1 = exp(log(it->sweight1) + laststream * log(_alpha));
	}
	segS.temp.SetCombine(frontSummary, backSummary);
}

template<typename FType, typename DType, typename IType, typename CType>
void OnlineQuantileNPunknownDrift<FType, DType, IType, CType>::ChoisePush(std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>>::iterator thisfi, int& adjustcount, int label, double v, double batchalpha) {
	int lastrecord0 = thisfi->second.first[1];
	int lastrecord1 = thisfi->second.first[2];
	//double cumw1 = 0, cumw0 = 0;
	if (c0 + c1 - lastrecord0 - lastrecord1 - 1 == 0) {//c0+c1 include current entry,last record is last none 0 record
		if (d != 0 && nrows == 1 && batchalpha) {
			BatchPenal(thisfi, batchalpha);
			thisfi->second.first.back() += 1;
		}
		thisfi->second.second.back().PushSparse(label, v, coverage, (double)_weight, 0);
		adjustcount = 1;
	}
	else {
		//for (std::vector<int>::iterator l = Yid.begin() + lastrecord0 + lastrecord1; l != Yid.end() - 1; ++l) {
		//	if (*l == 1) {
		//		//c1++;
		//		cumw1 = (1 - _rateI) * cumw1 + _rateI * 1;
		//		cumw0 = (1 - _rateI) * cumw0;
		//	}
		//	else {
		//		//c0++;				
		//		cumw0 = (1 - _rateI) * cumw0 + _rateI * 1;
		//		cumw1 = (1 - _rateI) * cumw1;
		//	}
		//}
		double cumw1, cumw0;
		if (penaltimes - thisfi->second.first.back() >= 1 && batchalpha) {
			int expon = penaltimes - thisfi->second.first.back();
			BatchPenal(thisfi, pow(batchalpha, expon));
			cumw1 = wtower1.back() - exp(log(wtower1[lastrecord0 + lastrecord1 - 1]) + (expon) * log(batchalpha)),
			cumw0 = wtower0.back() - exp(log(wtower0[lastrecord0 + lastrecord1 - 1]) + (expon) * log(batchalpha));
			thisfi->second.first.back() = penaltimes;
		}
		else {
			cumw1 = wtower1.back() - exp(log(wtower1[lastrecord0 + lastrecord1 - 1]) + (c0 + c1 - lastrecord0 - lastrecord1 - 1) * log(_alpha)),
			cumw0 = wtower0.back() - exp(log(wtower0[lastrecord0 + lastrecord1 - 1]) + (c0 + c1 - lastrecord0 - lastrecord1 - 1) * log(_alpha));
		}
		//if (thisfi->first==0 &&(cumw1<-30 || cumw0<-30)){//debug
		//	int check = 1;
		//}
		//double cumw1 = wtower1.back() - pow(1 - _rateI, c0 + c1 - lastrecord0 - lastrecord1 - 1) * wtower1[lastrecord0 + lastrecord1],
			//cumw0 = wtower0.back() - pow(1 - _rateI, c0 + c1 - lastrecord0 - lastrecord1 - 1) * wtower0[lastrecord0 + lastrecord1];
		//if(c1+c0==6939+4793){//debug
		//	if (label == 1) {
		//		context.second.front().PushSparse(0, 0, (c0 - lastrecord0) * coverage, cumw0);
		//		context.second.front().PushSparse(1, 0, (c1 - lastrecord1 - 1) * coverage, cumw1);
		//	}
		//	else {
		//		context.second.front().PushSparse(0, 0, (c0 - lastrecord0 - 1) * coverage, cumw0);
		//		context.second.front().PushSparse(1, 0, (c1 - lastrecord1) * coverage, cumw1);
		//	}
		//}
		//else{
		if (label == 1) {
			thisfi->second.second.back().PushSparse(0, 0, (c0 - lastrecord0) * coverage, cumw0, 0);
			thisfi->second.second.back().PushSparse(1, 0, (c1 - lastrecord1 - 1) * coverage, cumw1, 1);
			/*	context.second.back().PushSparse(0, 0, (c0 - lastrecord0) * coverage, context.first.first[0]);
				context.second.back().PushSparse(1, 0, (c1 - lastrecord1 - 1) * coverage, context.first.first[1]);*/
		}
		else {
			thisfi->second.second.back().PushSparse(0, 0, (c0 - lastrecord0 - 1) * coverage, cumw0, 0);
			thisfi->second.second.back().PushSparse(1, 0, (c1 - lastrecord1) * coverage, cumw1, 1);
			/*context.second.back().PushSparse(0, 0, (c0 - lastrecord0 - 1) * coverage, context.first.first[0]);
			context.second.back().PushSparse(1, 0, (c1 - lastrecord1) * coverage, context.first.first[1]);*/
		}
		//}
		if (d != 0 && nrows == 1 && batchalpha) {
			BatchPenal(thisfi, batchalpha);
			thisfi->second.first.back() += 1;
		}
		thisfi->second.second.back().PushSparse(label, v, coverage, (double)_weight, 0);
		adjustcount = c0 + c1 - lastrecord0 - lastrecord1;
		//adjustcount = 2;
	}
}

template<typename FType, typename DType, typename IType, typename CType>
void OnlineQuantileNPunknownDrift<FType, DType, IType, CType>::Finalize(double* binMatrix, double* miscore, double* chi2score, double* giniscore, int* varout, DType& bTime, DType& sTime, double batchalpha) {
	double n = c1 + c0;
	/*printf("\tstart Finalizing\n");
	fflush(stdout);*/
	debug10 = high_resolution_clock::now();
	high_resolution_clock::time_point getsumtime1, getsumtime2, finalsumtime1, finalsumtime2, findytime1, findytime2, findtime1, findtime2, distime1, distime2, finalbin1, finalbin2, erasetime1, erasetime2, bintime1, scoretime1, bintime2, scoretime2;
	std::chrono::duration<double, std::milli> getsumtime, finalsumtime, findytime, findtime, distime, finalbin, erasetime, bintime, scoretime;
	int si = 0, findy = 0, maxy = 0;

	for (std::set<int>::iterator vi = vars.begin(); vi != vars.end(); ++vi) {
		startT = high_resolution_clock::now();
		std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>>::iterator fi = sketch_collections.find(*vi);
	/*std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>>::iterator fi = sketch_collections.begin();
	while (fi != sketch_collections.end()) {
		startT = high_resolution_clock::now();*/
		DriftQSketch::SummaryContainer out;
		//int vi = fi->first;

		//if (vi == 471) {//debug
		//	int check = 1;
		//}
/* 		if (vi == 17) {
			int check = 1;
		} */
		//distime1 = high_resolution_clock::now();
		////int si = (int)std::distance(vars.begin(), vars.find(vi));
		//std::set<int>::iterator d = vars.begin();
		//int si = 0;
		//while (d != vars.end()) {
		//	if (*d == vi) {
		//		break;
		//	}
		//	else {
		//		d++;
		//		si++;
		//	}
		//}
		//distime2 = high_resolution_clock::now();
		//distime += distime2 - distime1;
		int lastrecord0 = fi->second.first[1];
		int lastrecord1 = fi->second.first[2];
		//double cumw1 = 0, cumw0 = 0;
		finalbin1 = high_resolution_clock::now();
		if (c0 + c1 - lastrecord0 - lastrecord1 > 0) {
			//if (maxy < c0 + c1 - lastrecord0 - lastrecord1) maxy = c0 + c1 - lastrecord0 - lastrecord1;

			findy++;

			//for (std::vector<int>::iterator l = Yid.begin() + lastrecord0 + lastrecord1; l != Yid.end(); ++l) {
			//	findytime1 = high_resolution_clock::now();
			//	if (*l == 1) {
			//		//c1++;
			//		cumw1 = (1 - _rateI) * cumw1 + _rateI * 1;
			//		cumw0 = (1 - _rateI) * cumw0;
			//	}
			//	else {
			//		//c0++;				
			//		cumw0 = (1 - _rateI) * cumw0 + _rateI * 1;
			//		cumw1 = (1 - _rateI) * cumw1;
			//	}
			//	findytime2 = high_resolution_clock::now();
			//	findytime += findytime2 - findytime1;
			//}
			//findytime1 = high_resolution_clock::now();   
			double a1 = (double)log(wtower1[lastrecord0 + lastrecord1 - 1]);
			double a2 = (double)(c0 + c1 - lastrecord0 - lastrecord1) * log(_alpha);
			double a5 = a1 + a2;
			double a3 = exp(a1 + a2);
			double a4 = wtower1.back();
			double cumw1, cumw0;
			if (penaltimes - fi->second.first.back() > 1 && batchalpha) {
				int expon = penaltimes - fi->second.first.back();
				BatchPenal(fi, pow(batchalpha, expon));
				cumw1 = wtower1.back() - exp(log(wtower1[lastrecord0 + lastrecord1 - 1]) + (expon)*log(batchalpha)),
				cumw0 = wtower0.back() - exp(log(wtower0[lastrecord0 + lastrecord1 - 1]) + (expon)*log(batchalpha));
				fi->second.first.back() = penaltimes;
			}
			else {
				cumw1 = wtower1.back() - exp(log(wtower1[lastrecord0 + lastrecord1 - 1]) + (c0 + c1 - lastrecord0 - lastrecord1) * log(_alpha)),
				cumw0 = wtower0.back() - exp(log(wtower0[lastrecord0 + lastrecord1 - 1]) + (c0 + c1 - lastrecord0 - lastrecord1) * log(_alpha));
			}
			//double cumw1 = wtower1.back() - pow(1 - _rateI, c0 + c1 - lastrecord0 - lastrecord1) * wtower1[lastrecord0 + lastrecord1],
				//cumw0 = wtower0.back() - pow(1 - _rateI, c0 + c1 - lastrecord0 - lastrecord1) * wtower0[lastrecord0 + lastrecord1];
			findytime2 = high_resolution_clock::now();
			//findytime += findytime2 - findytime1;
			fi->second.second.back().PushSparse(0, 0, (c0 - lastrecord0) * coverage, cumw0, 0);
			fi->second.second.back().PushSparse(1, 0, (c1 - lastrecord1) * coverage, cumw1, 1);
		}

		getsumtime1 = high_resolution_clock::now();
		if (fi->second.second.size() == 1) {
			fi->second.second.front().GetSummary(&out, 1.0 / (_factor));
		}
		else {
			DriftQSketch::SummaryContainer frontSummary, backSummary;
			if (fi->second.second.front().temp.data.size() == 0) {
				fi->second.second.front().GetSummary(&frontSummary, 1.0 / (_factor));
			}
			else {
				frontSummary = fi->second.second.front().temp;
			}
			int laststream;
			if (fi->second.first.back() == 1) {
				laststream = fi->second.first[5] - fi->second.first[3] + c0 + c1 - lastrecord0 - lastrecord1;
			}
			else {
				laststream = fi->second.first[4] - (fi->second.first[6] - fi->second.first[5] + 1) + c0 + c1 - lastrecord0 - lastrecord1;
			}
			//int laststream = fi->second.first[5] - fi->second.first[3];
			//{//debug
			//	int tempstream = 6025;
			//	for (std::vector<DriftQSketch::Entry>::iterator it = frontSummary.data.begin(); it != frontSummary.data.end(); ++it) {
			//		it->sweight0 = exp(log(it->sweight0) + tempstream * log(1 - _rateI));
			//		it->sweight1 = exp(log(it->sweight1) + tempstream * log(1 - _rateI));
			//	}
			//	double temp0 = frontSummary.data[0].sweight0 + fi->second.second.back().inqueue.queue[0].weight0;
			//	double temp1 = frontSummary.data[0].sweight1 + fi->second.second.back().inqueue.queue[0].weight1;
			//}
			for (std::vector<DriftQSketch::Entry>::iterator it = frontSummary.data.begin(); it != frontSummary.data.end(); ++it) {
				it->sweight0 = exp(log(it->sweight0) + laststream * log(_alpha));
				it->sweight1 = exp(log(it->sweight1) + laststream * log(_alpha));
			}
			fi->second.second.back().GetSummary(&backSummary, 1.0 / (_factor));
			DriftQSketch union_sketch;
			union_sketch.temp.SetCombine(frontSummary, backSummary);
			out = union_sketch.temp;
		}
		getsumtime2 = high_resolution_clock::now();
		getsumtime += getsumtime2 - getsumtime1;
		finalbin2 = high_resolution_clock::now();
		finalbin += finalbin2 - finalbin1;
		erasetime1 = high_resolution_clock::now();
		sketch_collections.erase(fi);
		//fi = sketch_collections.erase(fi);
		erasetime2 = high_resolution_clock::now();
		erasetime += erasetime2 - erasetime1;
		bintime1 = high_resolution_clock::now();
		vector<float> cl0(_numbin, 0), cl1(_numbin, 0);
		GetBinVector(cl0, cl1, out, n);

		for (int b = 0; b < _numbin; ++b) {
			binMatrix[_numbin * 2 * si + b] = cl0[b];
			binMatrix[_numbin * 2 * si + b + _numbin] = cl1[b];
		}
		bintime2 = high_resolution_clock::now();
		bintime += bintime2 - bintime1;
		stopT = high_resolution_clock::now();
		binTime += stopT - startT;
		//********end of sketch*************
		startT = high_resolution_clock::now();
		scoretime1 = high_resolution_clock::now();
		double chi2 = 0, gini = 0, mi = 0;
		GetScore(chi2, gini, mi, cl0, cl1);

		chi2score[si] = chi2;
		giniscore[si] = gini;
		miscore[si] = mi;
		scoretime2 = high_resolution_clock::now();
		scoretime += scoretime2 - scoretime1;
		stopT = high_resolution_clock::now();
		scoreTime += stopT - startT;
		//varout[si] = vi;
		varout[si] = *vi;
		si++;
		//fi++;
	}

	//int si = 0, findy = 0;
	//for (std::set<int>::iterator vi = vars.begin(); vi != vars.end(); ++vi) {
	//	startT = high_resolution_clock::now();
	//	DriftQSketch::SummaryContainer out;
	//	findtime1 = high_resolution_clock::now();
	//	std::unordered_map<int, std::pair<std::vector<int>, std::vector<DriftQSketch>>>::iterator fi = sketch_collections.find(*vi);
	//	findtime2 = high_resolution_clock::now();
	//	findtime += findtime2 - findtime1;

	//	int lastrecord0 = fi->second.first[1];
	//	int lastrecord1 = fi->second.first[2];
	//	double cumw1 = 0, cumw0 = 0;
	//	finalbin1 = high_resolution_clock::now();
	//	if (c0 + c1 - lastrecord0 - lastrecord1 > 0) {
	//		findy++;
	//		findytime1 = high_resolution_clock::now();
	//		for (std::vector<int>::iterator l = Yid.begin() + lastrecord0 + lastrecord1; l != Yid.end(); ++l) {
	//			if (*l == 1) {
	//				//c1++;
	//				cumw1 = (1 - _rateI) * cumw1 + _rateI * 1;
	//				cumw0 = (1 - _rateI) * cumw0;
	//			}
	//			else {
	//				//c0++;				
	//				cumw0 = (1 - _rateI) * cumw0 + _rateI * 1;
	//				cumw1 = (1 - _rateI) * cumw1;
	//			}
	//		}
	//		findytime2 = high_resolution_clock::now();
	//		findytime += findytime2 - findytime1;
	//		fi->second.second.back().PushSparse(0, 0, (c0 - lastrecord0) * coverage, cumw0);
	//		fi->second.second.back().PushSparse(1, 0, (c1 - lastrecord1) * coverage, cumw1);
	//	}

	//	finalsumtime1 = high_resolution_clock::now();
	//	if (fi->second.second.size() == 1) {
	//		fi->second.second.front().GetSummary(&out, 1.0 / (_factor));
	//	}
	//	else {
	//		DriftQSketch::SummaryContainer frontSummary, backSummary;
	//		if (fi->second.second.front().temp.data.size() == 0) {
	//			fi->second.second.front().GetSummary(&frontSummary, 1.0 / (_factor));
	//		}
	//		else {
	//			frontSummary = fi->second.second.front().temp;
	//		}
	//		int laststream = fi->second.first[4] - (fi->second.first[6] - fi->second.first[5] + 1);
	//		for (std::vector<DriftQSketch::Entry>::iterator it = frontSummary.data.begin(); it != frontSummary.data.end(); ++it) {
	//			it->sweight0 = exp(log(it->sweight0) + laststream * log(1 - _rateI));
	//			it->sweight1 = exp(log(it->sweight1) + laststream * log(1 - _rateI));
	//		}
	//		fi->second.second.back().GetSummary(&backSummary, 1.0 / (_factor));
	//		DriftQSketch union_sketch;
	//		union_sketch.temp.SetCombine(frontSummary, backSummary);
	//		out = union_sketch.temp;
	//	}
	//	finalsumtime2 = high_resolution_clock::now();
	//	finalsumtime += finalsumtime2 - finalsumtime1;
	//	finalbin2 = high_resolution_clock::now();
	//	finalbin += finalbin2 - finalbin1;
	//	erasetime1 = high_resolution_clock::now();
	//	sketch_collections.erase(fi);
	//	erasetime2 = high_resolution_clock::now();
	//	erasetime += erasetime2 - erasetime1;

	//	bintime1 = high_resolution_clock::now();
	//	vector<float> cl0(_numbin, 0), cl1(_numbin, 0);
	//	GetBinVector(cl0, cl1, out, n);
	//	for (int b = 0; b < _numbin; ++b) {
	//		binMatrix[_numbin * 2 * si + b] = cl0[b];
	//		binMatrix[_numbin * 2 * si + b + _numbin] = cl1[b];
	//	}
	//	bintime2 = high_resolution_clock::now();
	//	bintime += bintime2 - bintime1;
	//	stopT = high_resolution_clock::now();
	//	binTime += stopT - startT;
	//	//********end of sketch*************
	//	scoretime1 = high_resolution_clock::now();
	//	startT = high_resolution_clock::now();
	//	double chi2 = 0, gini = 0, mi = 0;
	//	GetScore(chi2, gini, mi, cl0, cl1);

	//	chi2score[si] = chi2;
	//	giniscore[si] = gini;
	//	miscore[si] = mi;
	//	scoretime2 = high_resolution_clock::now();
	//	scoretime += scoretime2 - scoretime1;
	//	stopT = high_resolution_clock::now();
	//	scoreTime += stopT - startT;

	//	si++;
	//}
	//printf("\ttime of finding index in vars: %f\n", distime.count() / vars.size());
	//fflush(stdout);
	//printf("\ttime of finding index in map: %f\n", findtime.count() / vars.size());
	//fflush(stdout);
	//printf("\ttime of finalBin: %f\n", finalbin.count() / vars.size());
	//fflush(stdout);
	////printf("\ttime of max unfilled: %d\n", maxy);
	////fflush(stdout);
	//printf("\ttime of going through Y: %f\n", findytime.count() / findy);
	//fflush(stdout);
	//printf("\ttime of get summary: %f\n", getsumtime.count() / vars.size());
	//fflush(stdout);
	////printf("\ttime of aggregate summary: %f\n", finalsumtime.count() / vars.size());
	////fflush(stdout);
	//printf("\ttime of erase: %f\n", erasetime.count() / vars.size());
	//fflush(stdout);
	//printf("\ttime of binning: %f\n", bintime.count() / vars.size());
	//fflush(stdout);
	//printf("\ttime of scoring: %f\n", scoretime.count() / vars.size());
	//fflush(stdout);
	debug11 = high_resolution_clock::now();
	debug12 = debug11 - debug10;
	bTime = binTime.count();
	sTime = scoreTime.count();
	//printf("\ttime of finalize: %f\n", debug12.count());
	//fflush(stdout);
	////varout = vars;
}

template<typename FType, typename DType, typename IType, typename CType>
template<typename Vtype>
void OnlineQuantileNPunknownDrift<FType, DType, IType, CType>::GetBinVector(Vtype& cl0, Vtype& cl1, DriftQSketch::SummaryContainer& insummary, int n) {
	double epsilonN = (double)1.0 / (_factor)*n;
	double est_bin_size = (double)n / _numbin;
	int current_bin = 0;
	double lastboundry = 0, boundry;
	int ispass = 0;
	LabelEntry lastentry = LabelEntry(0, 0, 0, 0, 0);
	float aprev_rmin = 0, bprev_rmin = 0;

	float x1 = 0, x0 = 0;
	for (auto& s : insummary.data) {
		x0 += lastentry.w0;
		x1 += lastentry.w1;
		cl0[current_bin] += lastentry.w0;
		cl1[current_bin] += lastentry.w1;
		if (ispass == 1) {
			if (s.value != lastentry.value) {
				boundry = round((current_bin + 1) * est_bin_size);
				boundry = (s.rmin - boundry) > (boundry - lastentry.rmax) ? (lastentry.rmax) : (s.rmin);
				lastboundry = boundry;
				while (boundry - round((current_bin + 1) * est_bin_size) >= 0) {
					++current_bin;
				}
				ispass = 0;
			}
		}
		else if (s.rmin >= round((current_bin + 1) * est_bin_size)) {// || lastentry.rmax >= (current_bin + 1)*est_bin_size) {
			if (s.value != lastentry.value) {
				boundry = round((current_bin + 1) * est_bin_size);
				boundry = (s.rmin - boundry) > (boundry - lastentry.rmax) ? lastentry.rmax : s.rmin;//(s.rmin + lastentry.rmax) / 2;					
				lastboundry = boundry;
				while (boundry - round((current_bin + 1) * est_bin_size) >= 0) {
					++current_bin;
				}
			}
			else ispass = 1;
		}

		lastentry = LabelEntry(s.rmin, s.rmax, s.sweight0, s.sweight1, s.value);
	}
	cl0[current_bin] += lastentry.w0;
	cl1[current_bin] += lastentry.w1;
}

template<typename FType, typename DType, typename IType, typename CType>
template<typename Vtype>
void OnlineQuantileNPunknownDrift<FType, DType, IType, CType>::GetScore(double& chi2, double& gini, double& mi, Vtype& cl0, Vtype& cl1) {
	double totalW0 = std::accumulate(cl0.begin(), cl0.end(), 0.0);
	double totalW1 = std::accumulate(cl1.begin(), cl1.end(), 0.0), totalW = totalW0 + totalW1;
	//chi2
	double nlc, nlc0, nlc1;
	double nlc_hat1, nlc_hat0, part0, part1;

	for (int j = 0; j < _numbin; j++) {
		nlc1 = cl1[j];// (*cl1)[j];
		nlc0 = cl0[j];// (*cl0)[j];
		nlc = nlc1 + nlc0;
		nlc_hat0 = totalW0 * nlc / (double)totalW;
		nlc_hat1 = totalW1 * nlc / (double)totalW;
		if (nlc_hat0 == 0) part0 = 0; else part0 = (nlc0 - nlc_hat0) * (nlc0 - nlc_hat0) / nlc_hat0;
		if (nlc_hat1 == 0) part1 = 0; else part1 = (nlc1 - nlc_hat1) * (nlc1 - nlc_hat1) / nlc_hat1;
		chi2 += part0 + part1;
	}

	//Gini
	double ah = 0, bh = totalW, ah0 = 0, ah1 = 0, bh0 = totalW0, bh1 = totalW1;
	double  pah, pbh, pah0, pah1, pbh0, pbh1, parta, partb;
	vector<double> gini_column;
	for (int j = 0; j < _numbin; j++) {
		if (ah == 0) parta = 0; else {
			pah = ah / (double)totalW;
			pah0 = ah0 / (double)ah;
			pah1 = ah1 / (double)ah;
			parta = pah * (1 - pow(pah0, 2) - pow(pah1, 2));
		}
		if (bh == 0) partb = 0; else {
			pbh = bh / (double)totalW;
			pbh0 = bh0 / (double)bh;
			pbh1 = bh1 / (double)bh;
			partb = pbh * (1 - pow(pbh0, 2) - pow(pbh1, 2));
		}
		gini_column.push_back(parta + partb);

		ah0 += cl0[j];// (*cl0)[j];
		ah1 += cl1[j];// (*cl1)[j];
		ah = ah0 + ah1;

		bh0 -= cl0[j];// (*cl0)[j];
		bh1 -= cl1[j];// (*cl1)[j];
		bh = bh1 + bh0;
	}
	gini = *std::min_element(gini_column.begin(), gini_column.end());

	//MI
	double px, py0 = totalW0 / (double)totalW, py1 = totalW1 / (double)totalW, pxy1, pxy0;

	for (int j = 0; j < _numbin; j++) {
		nlc1 = cl1[j];// (*cl1)[j];
		nlc0 = cl0[j];// (*cl0)[j];
		nlc = nlc1 + nlc0;
		px = nlc / (double)totalW;
		pxy0 = nlc0 / (double)totalW;
		pxy1 = nlc1 / (double)totalW;
		if (pxy0 == 0) part0 = 0; else part0 = pxy0 * log(pxy0 / (px * py0));
		if (pxy1 == 0) part1 = 0; else part1 = pxy1 * log(pxy1 / (px * py1));
		mi += part0 + part1;
	}
}

#endif#pragma once
