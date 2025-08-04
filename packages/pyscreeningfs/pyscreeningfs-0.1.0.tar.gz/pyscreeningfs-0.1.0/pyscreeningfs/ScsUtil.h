#ifndef _SCS_UTIL_H
#define _SCS_UTIL_H
#pragma warning(disable:4786)
#pragma warning(disable:4996)

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include "SimpleMatrix.h"
#include <iostream>
#include <vector>
#include <list>
#include <string>
#include <cmath>
#include <cfloat>
#include <cstdint>
#include <stdio.h>
#include <string.h>
#include <set>
#include <map>
#include <functional>
#include <fstream>
#include <sstream>
#include "Point.h"
#include "VectorUtil.h"
#include <algorithm>
#include <typeinfo> 
#include <iterator>

#define EPSILON	1e-10								//definition of minim value	
#define LPI	3.14159265359

extern char fnGlobalLogfile[261];	

std::string GetCurrentTimeString();
int64_t Rand64();
void	ConsumeWhiteSpace(FILE *pFile);
double	AUC(std::vector<float> &det, std::vector<float> &fp);
bool	AddLines(const char *fnDest, const char *fnSrc);
void	AppendAndAdd(std::vector<std::string> &pos, const char *str1, const char *str2, float perc);
void	AppendAndDuplicate(std::vector<std::string> &pos, const char *str1, const char *str2);
double	BhattacharyyaDistance(std::vector<double> &p, std::vector<double> &q);
void	Choose(std::vector<int> &idx, int n,int k);
template<class Tp>
bool	Choose(std::vector<Tp> &out, std::vector<Tp> &in, int k);
void	ChooseSplit(std::vector<int> &idx, std::vector<int> &v,int k);
void	ClearFile(const char * filename);
void	CopyFile(const char *to, const char *from);
int		CountLines(const char *filename);
void	CreateCrossValFold(std::vector<int> &train, std::vector<int> &test, int nObs, int nFolds, int iFold);
bool	CreateCrossValFolds(char *filenames, int nfolds);
template<class Tp>
bool	DlmRead(FILE *f, std::vector<std::vector<Tp> > &v, const char *dlm);
template<class Tp>
bool	DlmRead(FILE *f, SimpleMatrix<Tp> &M, const char *dlm);
template<class Tp>
bool	DlmRead(const char *name, std::vector<std::vector<Tp> > &v, const char *dlm);
template<class Tp>
bool	DlmRead(char *name,std::vector<std::string> &header, std::vector<std::vector<Tp> > &v, const char *dlm);
template<class Tp>
bool    DlmWrite(char * filename,const Tp &M, const char * fmt="%g", char dlm=',');
template<class Tp>
bool	DlmWrite(FILE *f, const std::set<Tp> &values, const char *fmt, char sep, int writeEol=1);
template<class Tp>
bool	DlmWrite(FILE *f, const std::vector<Tp> &values, const char *fmt="%g", char sep=',', int writeEol=1);
template<class Tp>
void	DlmWrite(FILE * f, const Tp *values, int nVal, const char *fmt="%g", char sep=',', int writeEol=1);
template<class Tp>
void	DlmWrite(FILE *f, const std::vector<std::vector<Tp> > &values, const char *fmt="%g", char sep=',');
template<class Tp>
void    DlmWrite(FILE *f, const SimpleMatrix<Tp> &M, const char *fmt, char dlm);
template<class Tp>
void	Dropout(std::vector<Tp> &v, double prob);
float	Entropy(std::vector<float> &prob);
float	EqualErrorRate(std::vector<float> &det, std::vector<float> &fa);
float	EqualErrorRate(std::vector<float> *roc);
void	FindFirstName(char *name, char *root, char *ext);
void	FindPairsSameLabel(std::vector<std::pair<int,int> > &pairs, std::vector<int> &label);
void	FindSameLabel(std::vector<std::vector<int> > &qids, std::vector<std::string> &label);
void	GetFileNameOnly(char * lpszDest, const char * lpszSour);
void	GetFileNameWithExtensionOnly(char * lpszDest, const char * lpszSour);
void	GetFirstWord(char *str_dest, char *str_sour);
void	GetFirstWord(char * lpszDest, char * lpszSour, char cSeprator, bool bChangeSour=false);
void	GetLastWord(char * lpszDest, char * lpszSour, char cSeprator, bool bChangeSour=false);
void	GetFirstField(char *str_dest, char *str_sour, char dlm);
bool    Glob(std::vector<std::string> &file_list, std::string path,int layer);
bool	InBounds(int rows,int cols, int i, int j);
int		IntClose(double x);
template<class Tp>
void	KeepExisting(std::vector<Tp> &out, std::vector<Tp> &in, std::vector<Tp> &all);
bool	KeepNumbersOnly(const char *fnout, const char *fnin);
void	KeepFilenameOnly(std::vector<std::string> &out, std::vector<std::string> &in);
template<class Tp>
bool	LineRead(std::vector<Tp> &v, const char *name, const char *dlm);
template<class Tp>
bool	LineRead(std::vector<Tp> &v, FILE *f,  const char *dlm, int maxlen);
void	LineSkip(FILE *f);
template<class Tp>
bool	Log2File(char * filename, const std::vector<Tp> &values,const char *fmt="%g", char sep=',');
bool	Log2File(char *filename, const char * format, ...);
template<class Tp>
void	MergeSets(std::vector<Tp> &out,std::vector<Tp> &s1,std::vector<Tp> &s2);
template<class Tp>
void	MergeSetsSVM(std::vector<Tp> &out,std::vector<Tp> &s1,std::vector<Tp> &s2);
double	NormRand();
bool    Permute(int *v, std::vector<int> &result, const int start, const int n);
void	PrintOut(const char * format, ...);
bool	PrintOut(std::vector<float> &values, const char *fmt="%g", char sep=',');
template<class Tp>

double	Prob(int j,Tp *p, int np);
template<class Tp>
bool PutIntoVectorF(std::vector<Tp> &out, const char *str, const char *dlm);
template<class Tp>
bool PutIntoVectorI(std::vector<Tp> &out, const char *str, const char *dlm);
inline bool	PutIntoVector(std::vector<int> &out, const char *str, const char * dlm){return PutIntoVectorI(out,str,dlm);}
inline bool	PutIntoVector(std::vector<unsigned char> &out, const char *str, const char *dlm){return PutIntoVectorI(out,str,dlm);}
inline bool	PutIntoVector(std::vector<unsigned short> &out, const char *str, const char *dlm){return PutIntoVectorI(out,str,dlm);}
inline bool	PutIntoVector(std::vector<float> &out, const char *str, const char * dlm){return PutIntoVectorF(out,str,dlm);}
inline bool	PutIntoVector(std::vector<double> &out, const char *str, const char * dlm){return PutIntoVectorF(out,str,dlm);}
bool	PutIntoVector(std::vector<double> &out, int* label_init, char *str, const char dlm);
void	PutIntoVector(std::vector<std::string> &vstrings, const char *str, const char *dlm );
int		RandInt(int n);
double	RandDbl(double d);
template<class Tp,class Tpy>
bool	ReadTextLine(std::vector<Tp> &x, Tpy &y, FILE *f,const char *dlm,int posY, int maxlen);
template<class Tp>
bool	ReadVectorByLine(const char *file, std::vector<Tp> &vsampl, float subSampleProb=2.f);
template<class Tp>
bool	ReadLineOfPairs(std::vector<Tp> &x, Tp &y, int &qid, FILE *f);
void	RenameExtension(char *path, char *ext);
int		Round(float x);
bool	ReadPoints(std::vector<Pointf> &pts,char *filename);
bool	ReadAsf(std::vector<Pointf> &pts, const char *name);
bool	ReadMod(std::vector<Pointf> &pts, const char *name);
bool	ReadLinePoints(std::vector<Pointf> &pts,char * name);
bool	ReadLines(std::vector<std::string> &vsampl, const char *file, int maxNo=0);
bool    ReadLines(const char* filename, std::vector<std::string> &vsampl, std::vector<int>& num);
bool    ReadLines(const char* filename, std::vector<std::string> &vsampl);
bool	ReadLines(std::vector<std::string> &vsampl, const char *file, float subSampleProb);
template<class Tp,class TpY>
bool ReadSvm(std::vector<std::vector<Tp>> &x, std::vector<TpY> &y, const char *name, const char *dlm);
template<class Tp,class TpY>
bool ReadSvm(std::vector<std::vector<std::pair<int,Tp>>> &x, std::vector<TpY> &y, const char *name, const char *dlm);
template<class Tp, class TpY>
bool ReadSvmBatch(std::vector<std::vector<std::pair<int, Tp>>> &x, std::vector<TpY> &y, const char *name, const int batchsize, const char *dlm);
template<class Tp>
void	RemoveDuplicates(std::vector<Tp> &out, std::vector<Tp> &in);
double  RSquare(int nObs, double sumy, double sumyy, double sumdd);
template<class Tp>
int		Sample(Tp *p, int np);
void	SampleBernoulli(std::vector<int> &out, int n, double prob);
void	SampleBernoulliIdx(std::vector<int> &out, int n, double prob);
bool	SaveLines(const char *file, std::vector<std::string> &vsampl, int saveEol=1);
template<class Tp>
bool	SaveLines(const char *file, const std::vector<Tp> &vsampl, const char *fmt);
template<class Tp>
bool	SaveVectorByLine(const char *file, std::vector<Tp> &vsampl, bool overwrite=false);
bool	SaveToFile(char *name, std::vector<Pointf> &pts);
double  Sigmoid(double x);
int		Sign( int n );
void	SplitPathFileNameExtension(char *path, char *filename,char *ext, const char * lpszSour);
bool	StringEndsCaseInsensitive(const char * string, const char * ending);
bool	StripLinesTok( char *fout, char *fin, const char *dlm);
bool	SubSample(char *fileOut, char *fileIn, double prob);
int		TestVars(std::vector<int> &sel, const std::set<int> &strue);
int		TestVars(std::vector<int> &det, std::vector<int> &sel, const std::set<int> &strue);

//
//template<class Tp>
//bool LoadItemsByImage(std::vector<std::vector<Tp>> &db, const char *filename, std::vector<std::string> &names, int addExtension){
//	char stritem[100001];
//	std::vector<Tp> list;
//	std::map<std::string, int> nameOrder;
//	Tp item;
//	string name = "\0";
//	FILE *fitems = fopen(filename, "rt");
//
//	if (fitems == NULL){
//		printf("%s not found\n", filename);
//		return false;
//	}
//
//	int i = 0, ni = (int)names.size();
//	for (; (i < ni); i++){
//		if (addExtension)
//			nameOrder[names[i] + ".jpg"] = i;
//		else
//			nameOrder[names[i]] = i;
//	}
//
//	db.resize(ni);
//	i=0;
//	while (!feof(fitems)){
//		if (fgets(stritem, 100000, fitems) == 0) break;
//		item.ReadFromLine(stritem);
//		if (name == "\0") name = item._name;
//		if (item._name == name){
//			list.push_back(item);
//		}
//		else{
//			if (nameOrder.find(name) != nameOrder.end()){
//				db[nameOrder[name]] = list;
//				i++;
//			}
//			name = item._name;
//			printf(" Loading instances from image %s\n", name.c_str());
//			list.clear();
//			list.push_back(item);
//		}
//
//	}
//	if (nameOrder.find(name) != nameOrder.end()){
//		db[nameOrder[name]] = list;
//		i++;
//	}
//	fclose(fitems);
//	printf("\n Loaded items for %d images.\n", i);
//	return true;
//}

template<class Tp>
void AppendAndAdd(std::vector<std::string> &pos, std::vector<Tp> &y, const char *str1, const char *str2, float perc){
	srand(0);
	int n=(int)pos.size();
	pos.reserve((int)(n*perc*1.1));
	y.reserve((int)(n*perc*1.1));
	for (int i=0;i<n;i++){
		if (RandDbl(1)<perc){
			std::string st=pos[i];
			st.append(str2);
			pos.push_back(st);
			y.push_back(y[i]);
		}
	}
	for (int i=0;i<n;i++)
		pos[i].append(str1);
}

template<class Tp>
void NormRand(std::vector<Tp> &x, int n){
	x.resize(n);
	for (int i=0;i<n;i++)
		x[i]=(Tp)NormRand();
}

template<class Tp>
int TestVars(Tp *sel, int n, const std::set<int> &strue){
	// return how many of the elements of sel are found
	int i,kstar=(int)strue.size(),nfound=0;
	for (i=0;i<n;i++){
		if (strue.find((int)sel[i])!=strue.end())
			nfound++;
	}
	return nfound;
}

template<class Tp, class Tp2>
void DoubleSort(size_t n, Tp *x, Tp2 *y){
	//sort the corresponding arays x and y of same length according to the array x
    std::vector<std::pair<Tp, Tp2>> xy(n);

    //copy into pairs
    for( size_t i = 0; i<n; ++i){
      xy[i].first  = x[i];
      xy[i].second = y[i];
    }

	std::sort(xy.begin(), xy.end());

    //Place back into arrays
    for( size_t i = 0; i<n; ++i){
      x[i] = xy[i].first;  
      y[i] = xy[i].second;
    }
}

template<class Tp, class Tp2>
void ComputeIntegralImage(Tp* iip, const Tp2 *data, int width, int height){
	std::vector<Tp> tempi(width);
	Tp * temp = &tempi[0];
	//compute first term
	iip[0] = temp[0] = data[0];
	//compute first row
	for (int x = 1; x < width; x ++){ 
		temp[x] = temp[x-1] + (Tp)data[x];
		iip[x] = temp[x];
	}
	for (int y = 1, yAddr = width; y < height; y ++, yAddr += width){
		//compute first column
		temp[0] = (Tp) data[yAddr];
		iip[yAddr] = iip[yAddr - width] + temp[0];
		for (int x = 1; x < width; x ++)	{
			int addr = x + yAddr;
			temp[x] = temp[x-1] + (Tp) data[addr];
			iip[addr] = iip[addr - width] + temp[x];
//assert(iip[addr]>=0);
		}
	}
}

template<class Tp>
Tp RectSum(SimpleMatrix<Tp> &ii, const int x0, const int y0, const int x1, const int y1){
	Tp a,b,c,d = ii(y1,x1);

	if (x0== 0||y0==0)
		a = 0;
	else
		a = ii(y0-1,x0-1);

	if (y0== 0)
		b = 0;
	else
		b = ii(y0-1,x1);

	if (x0== 0)
		c = 0;
	else
		c = ii(y1,x0-1);

	return (a + d - b - c);
}

template<class Tp>
void Dropout(Tp &vbegin, Tp &vend, double prob){
	for (Tp i=vbegin;i!=vend;++i)
		if (RandDbl(1)<=prob)
			*i=0;
}

template<class Tp>
int RandomlySubsample(std::vector<Tp> &out, const std::vector<Tp> &in, const int num_topick){
	std::vector<int> idx;
	if (((int)in.size()) < num_topick){
		out = in;
		return (int)out.size();
	}
	Choose(idx,(int)in.size(),num_topick);
	out.resize(num_topick);
	for (int i=0; i<num_topick; i++)
		out[i]=in[idx[i]];
	return (int)out.size();
}

template <class Tp>
void SmoothBins(std::vector<Tp> &bins, int numBins){
	std::vector<Tp> binsT;
	int i=0;

	binsT.resize(numBins+1);
	binsT[i] = (3*bins[i]+bins[i+1])/4;
	for (i=1; i<(numBins); ++i){
		binsT[i] = (bins[i-1]+2*bins[i]+bins[i+1])/4;
	}
	i=numBins;
	binsT[i] = (3*bins[i]+bins[i-1])/4;
	bins=binsT;
}

template <class Tp>
struct LexOrder:public std::binary_function<std::pair<std::string,Tp>,std::pair<std::string,Tp>, bool> {
	bool operator()(const std::pair<std::string,Tp> &a, const std::pair<std::string,Tp> &b) const{
		return strcmp(a.first.c_str(),b.first.c_str())<0;
	}
};

template <class Tp1,class Tp2>
struct InvFirstOrder:public std::binary_function<std::pair<Tp1,Tp2>,std::pair<Tp1,Tp2>, bool> {
	bool operator()(const std::pair<Tp1,Tp2> &a, const std::pair<Tp1,Tp2> &b) const{
		return a.first>b.first;
	}
};

template <class Tp1,class Tp2>
struct InvSecondOrder:public std::binary_function<std::pair<Tp1,Tp2>,std::pair<Tp1,Tp2>, bool> {
	bool operator()(const std::pair<Tp1,Tp2> &a, const std::pair<Tp1,Tp2> &b) const{
		return a.second>b.second;
	}
};

template <class Tp1,class Tp2>
struct FirstOrder:public std::binary_function<std::pair<Tp1,Tp2>,std::pair<Tp1,Tp2>, bool> {
	bool operator()(const std::pair<Tp1,Tp2> &a, const std::pair<Tp1,Tp2> &b) const{
		return a.first<b.first;
	}
};

template <class Tp1,class Tp2>
struct SecondOrder:public std::binary_function<std::pair<Tp1,Tp2>,std::pair<Tp1,Tp2>, bool> {
	bool operator()(const std::pair<Tp1,Tp2> &a, const std::pair<Tp1,Tp2> &b) const{
		return a.second<b.second;
	}
};

template <class Tp>
void GetROC(std::vector<float> &det, std::vector<float> &fa, std::vector<float> &p, std::vector<Tp> &y, int nThr){
	int	ndet=0,nfa=0,npos=0,nneg=0,t;
	float thr;
	det.assign(nThr,0);
	fa=det;
	float startThr,endThr,stepThr;
	GetMinMax(startThr,endThr,p);
	endThr+=0.1f;
	stepThr=(endThr-startThr)/nThr;
	int nObs=(int)p.size();
	for (int n=0;n<nObs;n++){
		if (y[n]>0){
			npos++;
			for (t=0;t<nThr;t++){
				thr=startThr+t*stepThr;
				if (p[n]>=thr)
					det[t]++;
			}
		}
		else{
			nneg++;
			for (t=0;t<nThr;t++){
				thr=startThr+t*stepThr;
				if (p[n]>=thr)
					fa[t]++;
			}
		}
	}
	det/=(float)npos;
	fa/=(float)nneg;
}

template <class Tp>
void GetROC(std::vector<float> &det, std::vector<float> &fa, std::vector<float> &thrs, std::vector<float> &p, std::vector<Tp> &y, int nThr){
	int	ndet=0,nfa=0,npos=0,nneg=0,t;
	float thr;
	det.assign(nThr,0);
	fa=det;
	thrs=det;
	float startThr,endThr,stepThr;
	GetMinMax(startThr,endThr,p);
	endThr+=0.1f;
	stepThr=(endThr-startThr)/nThr;
	int nObs=(int)p.size();
	for (t=0;t<nThr;t++)
		thrs[t]=startThr+t*stepThr;
	for (int n=0;n<nObs;n++){
		if (y[n]>0){
			npos++;
			for (t=0;t<nThr;t++){
				thr=startThr+t*stepThr;
				if (p[n]>=thr)
					det[t]++;
			}
		}
		else{
			nneg++;
			for (t=0;t<nThr;t++){
				thr=startThr+t*stepThr;
				if (p[n]>=thr)
					fa[t]++;
			}
		}
	}
	det/=(float)npos;
	fa/=(float)nneg;
}

template <class Tp>
int InsertCandidate( std::list<Tp> &detected, const Tp &box, float &probThr, int nMaxCandidate, double minProb ){
	if( box._prob < minProb && box._prob < probThr )
		return -1;
	// Only use detection score to select positives.
	if( nMaxCandidate == 0 ){
		if( box._prob > minProb )
			detected.push_back( box );
		return 0;
	}
	
	typename std::list<Tp>::iterator	iter;
	int nCandidate = 0;
	for( iter = detected.begin(); iter != detected.end(); iter++ ){
		if( nCandidate == nMaxCandidate-1 )
			probThr = iter->_prob;

		if( box._prob >= iter->_prob )
			break;
		if( nCandidate >= nMaxCandidate && box._prob <= minProb )
			break;
		nCandidate ++;
	}
	if( nCandidate < nMaxCandidate || box._prob > minProb )
		detected.insert( iter, box );
	return 0;
}

template<class Tp>
bool Choose(std::vector<Tp> &out, std::vector<Tp> &in, int k){
	std::vector<int> idx;
	int n=(int)in.size();
	if (n<k)
		return false;
	Choose(idx,n,k);
	out.resize(k);
	std::sort(idx.begin(),idx.end());
	for (int i=0;i<k;i++)
		out[i]=in[idx[i]];
	return true;
}

template<class Tp>
void Permute(std::vector<Tp> &v){ 
	// Sample k random numbers w/o replacement from 0...n-1 and put them in idx
	// Ref: Knuth, D. E., The Art of Computer Programming, Vol. 2:
	// Seminumerical Algorithms. London: Addison-Wesley, 1969.
	int i,j,n=(int)v.size(); 
	Tp tmp;
	for (i=0;i<n;i++){
		j=RandInt(n-i);
		tmp=v[n-i-1];	//swap v[j] with v[n-i-1]
		v[n-i-1]=v[j];
		v[j]=tmp;
	}
}

template<class Tp>
bool BinWrite(const char *name, SimpleMatrix<Tp> &M){
	std::ofstream strm;
	int n[2]={M.nx(),M.ny()};
	strm.open(name, std::ios::out|std::ios::binary);
	if (strm.fail())
		return false;
	strm.write((char*)n,sizeof(int)*2);
	strm.write((char*)&M[0], sizeof(Tp)*M.size());
	strm.close();
	return true;
}

template<class Tp>
bool BinRead(SimpleMatrix<Tp> &M, const char *name){
	std::ifstream strm;
	int n[2];
	strm.open(name, std::ios::in|std::ios::binary);
	if (strm.fail())
		return false;

	strm.read((char*)n, sizeof(int)*2);
	M.SetDimension(n[1],n[0]);
	strm.read((char*)&M[0], sizeof(Tp)*n[0]*n[1]);
	if (strm.fail())
		return false;
	strm.close();
	return true;
}

template<class Tp>
bool DlmRead(FILE *f, SimpleMatrix<Tp> &M, const char *dlm){
	std::vector<std::vector<Tp> > vm;
	DlmRead(f,vm,dlm);
	if (vm.size()==0)
		return false;
	int i,j,nx=(int)vm[0].size(),ny=(int)vm.size();
	M.SetDimension(ny,nx);
	for (i=0;i<ny;i++)
		for (j=0;j<nx;j++)
			M(i,j)=vm[i][j];
	return true;
}

template<class Tp>
bool DlmRead(char * filename, SimpleMatrix<Tp> &M, const char *sep){
	FILE *f=fopen(filename,"rt");
	if (f!=NULL){
		DlmRead(f,M,sep);
		fclose(f);
		return true;
	}
	return false;
}

template<class Tp>
bool DlmWrite(FILE *f, const std::vector<Tp> &values, const char *fmt, char sep, int writeEol){
	DlmWrite(f,&values[0],(int)values.size(),fmt,sep,writeEol);
	return true;
}

template<class Tp>
void DlmWrite(FILE *f, const std::set<Tp> &values, const char *fmt, char sep, int writeEol){
	typename std::set<Tp>::iterator si,se=values.end();
	int i=0,nVal=(int)values.size();
	for (si=values.begin();si!=se;++si){
		Tp v=*si;
		int d=(int)v;
		if ((Tp)d==v){
			fprintf(f,"%d",d);
		}
		else
			fprintf(f,fmt,v);
		if (i<nVal-1)
			fprintf(f,"%c",sep);	
		i++;
	}
	if (writeEol!=0)
		fprintf(f,"\n");
}

template<class Tp>
void DlmWrite(FILE * f, const Tp *values, int nVal, const char *fmt, char sep, int writeEol){
	// does not necessarily write \n at the end
	int i,d;
	for (i=0;i<nVal;i++){
		Tp v=values[i];
		d=(int)v;
		if ((Tp)d==v){
			fprintf(f,"%d",d);
		}
		else
			fprintf(f,fmt,v);
		if (i<nVal-1)
			fprintf(f,"%c",sep);
	}
	if (writeEol!=0)
		fprintf(f,"\n");
}

template<class Tp>
bool SaveLines(const char *filename, const std::vector<Tp> &values, const char *fmt){
	FILE *f=fopen(filename, "w" );
	if (f==0)
		return false;
	int d,nVal=(int)values.size();
	for (int i=0;i<nVal;i++){
		Tp v=values[i];
		d=(int)v;
		if ((Tp)d==v)
			fprintf(f,"%d",d);
		else
			fprintf(f,fmt,v);
		fprintf(f,"\n");
	}
	fclose(f);
	return true;
}

template<class Tp>
void DlmWrite(FILE *f, const std::vector<std::vector<Tp> > &values, const char *fmt, char sep){
	for (size_t i=0;i<values.size();i++){
		DlmWrite(f,&values[i][0],(int)values[i].size(),fmt,sep,1);
	}
}

template<class Tp>
void DlmWrite(FILE *f, const SimpleMatrix<Tp> &M, const char *fmt, char sep){
	int i,r=M.rows(),c=M.cols();
	for(i=0;i<r;i++){
		DlmWrite(f,&M(i,0),c,fmt,sep,1);
	}
}

template<class Tp>
bool DlmWrite(char * filename, const Tp &M, const char * fmt, char dlm){
	FILE *f=fopen(filename, "w" );
	if (f==0)
		return false;
	DlmWrite(f,M,fmt,dlm);
	fclose( f );
	return true;
}

template<class Tp>
bool Log2File(char * filename, const std::vector<Tp> &values, const char *fmt, char sep){
	FILE *f=fopen(filename,"a+");
	if (f==NULL)
		return false;
	DlmWrite(f,&values[0],(int)values.size(),fmt,sep);
	fclose(f);
	return true;
}

template<class Tp>
bool LineRead(std::vector<Tp> &v, const char *name, const char *dlm){
	FILE *f=fopen(name,"rt");
	if (f==NULL)
		return false;
	LineRead(v,f,dlm,100000);
	fclose(f);
	return true;
}

template<class Tp>
bool LineRead(std::vector<Tp> &v, FILE *f, const char *dlm, int maxlen){
	static std::vector<char> line(maxlen);
	line.assign(maxlen,0);
	if (fgets(&line[0], maxlen, f)==0)
		return false;
	PutIntoVector(v, &line[0],dlm);
	return true;
}

template<class Tp>
bool DlmRead(const char *name, std::vector<std::vector<Tp> > &v, const char * dlm){
	FILE *f=fopen(name,"rt");
	v.clear();
	if (f==0)
		return false;
	DlmRead(f,v,dlm);
	fclose(f);
	return true;
}

template<class Tp>
bool DlmRead(FILE *f, std::vector<std::vector<Tp> > &v, const char *dlm){
	char *line=new char[1000000];
	std::vector<Tp> vf;
	v.clear();
	while(!feof(f)){
		if (fgets(line, 1000000, f)==0)
			break;
		PutIntoVector(vf, line,dlm);
		v.push_back(vf);
	}
	delete []line;
	return true;
}

template<class Tp>
bool DlmRead(FILE *f, std::vector<std::vector<Tp> > &v, const char *dlm, int nrows){
	char *line=new char[1000000];
	std::vector<Tp> vf;
	v.reserve(nrows);
	v.clear();
	for (int i=0;i<nrows;i++){
		if (fgets(line, 1000000, f)==0)
			break;
		PutIntoVector(vf, line,dlm);
		v.push_back(vf);
	}
	delete []line;
	return true;
}

template<class Tp>
bool DlmRead(char *name,std::vector<std::string> &header, std::vector<std::vector<Tp> > &v, char dlm){
	const char pDlmStr[] = { dlm, '\0' };

	std::vector<Tp> vf;
	char *line=new char[100000];
	char str1[100000];
	FILE *f=fopen(name,"rt");
	if (f==0)
		return false;
	fgets(line, 100000, f);	
	GetFirstField(str1, line, '\n');
	if (str1 != NULL)
		PutIntoVector(header, str1, pDlmStr);
	v.clear();
	while(!feof(f)){
		if (fgets(line, 100000, f)==0)
			break;
		PutIntoVector(vf, line,dlm);
		v.push_back(vf);
	}
	delete []line;
	fclose(f);
	return true;
}

template<class Tp,class Tpy>
bool ReadTextLine(std::vector<Tp> &x, Tpy &y, FILE *f, const char *dlm, int posY, int maxlen){
	static std::vector<Tp> v;
	if (!LineRead(v,f,dlm,maxlen))
		return false;
	int i,n=(int)v.size();
	if (n<=1)
		return false;
	if (posY<0)
		posY=n-1;
	x.resize(n-1);
	for (i=0;i<posY;i++)
		x[i]=v[i];
	if (typeid(int)==typeid(Tpy))
		y=(int)(v[posY]+0.5);
	else
		y=(Tpy)v[posY];
	for (i=posY+1;i<n;i++)
		x[i-1]=v[i];
	return true;
}

template<class Tp>
bool ReadLineOfPairs(std::vector<Tp> &x, Tp &y, int &qid, FILE *f){
	static std::vector<std::string> v;
	static std::vector<Tp> v1;
	if (!LineRead(v,f," ",100000))
		return false;
	int i,j,n=(int)v.size();
	if (n<=2)
		return false;
	y=(Tp)atof(v[0].c_str());
	qid=atoi(v[1].c_str()+4);
	x.assign(n-2,0);
	for (i=2;i<n;i++){
		if(v[i]=="#")
			break;
		PutIntoVector(v1,v[i].c_str(),":");
		j=(int)v1[0]-1;
		while(j>=x.size())
			x.push_back(0);
		x[j]=v1[1];
	}
	return true;
}

template<class Tp>
bool ReadLineOfPairs(std::vector<Tp> &x, Tp &y, std::string &qid, FILE *f){
	static std::vector<std::string> v;
	static std::vector<Tp> v1;
	if (!LineRead(v,f," ",100000))
		return false;
	int i,j,n=(int)v.size();
	if (n<=2)
		return false;
	y=(Tp)atof(v[0].c_str());
	qid=v[1];
	x.assign(n-2,0);
	for (i=2;i<n;i++){
		if(v[i]=="#")
			break;
		PutIntoVector(v1,v[i].c_str(),":");
		j=(int)v1[0]-1;
		if (j<0)
			break;
		while(j>=(int)x.size())
			x.push_back(0);
		x[j]=v1[1];
	}
	return true;
}

template<class Tp>
void SaveVectorByLine(FILE *pfile, std::vector<Tp> &vsampl){
	char	str_temp[100001];
	int i,n=(int)vsampl.size();
	
	for (i=0;i<n;i++){
		vsampl[i].SaveToLine(str_temp);
		fprintf(pfile,"%s\n",str_temp);
	}
}

template<class Tp>
bool SaveVectorByLine(const char *file, std::vector<Tp> &vsampl, bool overwrite){
	FILE	*pfile;
	char	str_temp[100001];
	int i,n=(int)vsampl.size();
	
	if (overwrite)
		pfile = fopen(file, "wt");
	else
		pfile = fopen(file, "a+t");
	if (pfile == NULL)
		return false;
	
	for (i=0;i<n;i++){
		vsampl[i].SaveToLine(str_temp);
		fprintf(pfile,"%s\n",str_temp);
	}
	
	fclose(pfile);
	return true;
}

template<class Tp>
bool ReadVectorByLine(const char *file, std::vector<Tp> &vsampl, float subSampleProb){
	FILE	*pfile;
	char	str_temp[100001];
	
	pfile = fopen(file, "rt");
	if (pfile == NULL)
		return false;
	
	Tp candidate;
	
	long counter = 0; // for debugging
	while (!feof(pfile)){
		counter++;
		if (fgets(str_temp, 100000, pfile)==0)
			break;
		if (RandDbl(1)<subSampleProb&&candidate.ReadFromLine(str_temp)){
			vsampl.push_back(candidate);
		}
	}

	fclose(pfile);
	return true;
}

template<class Tp>
void SubSample( std::vector<Tp> &out,std::vector<Tp> &vsampl, double prob){
	int i,n=(int)vsampl.size();
	out.clear();
	out.reserve((int)(n*prob*1.1));
	for (i=0;i<n;i++){
		if (RandDbl(1)<prob)
			out.push_back(vsampl[i]);
	}
}

template<class Tp>
int Sample(Tp *p, int np){
	int i;
	Tp pr=0;
	Tp a=(Tp)RandDbl(1);
	for (i=0;i<np;i++){
		pr=pr+p[i];
		if (a<=pr)
			return i;
	}
	return np;
}

template<class Tp>
double Prob(int j,Tp *p, int np){
	int i;
	Tp sum=0;
	for (i=0;i<np;i++)
		sum+=p[i];
	return p[j]/sum;
}

template<class Tp>
void KeepExisting(std::vector<Tp> &out, std::vector<Tp> &in, std::vector<Tp> &all){
	// keep elements from in that exist in all
	std::set<Tp> as;
	typename std::set<Tp>::iterator ae;
	for (int i=0;i<(int)all.size();i++)
		as.insert(all[i]);
	ae=as.end();
	out.clear();
	for (int i=0;i<(int)in.size();i++)
		if (as.find(in[i])!=ae)
			out.push_back(in[i]);
}

template<class Tp>
void RemoveDuplicates(std::vector<Tp> &out, std::vector<Tp> &in){
	std::set<Tp> s;
	typename std::set<Tp>::iterator si;
	for (int i=0;i<(int)in.size();i++)
		s.insert(in[i]);
	out.clear();
	for (si=s.begin();si!=s.end ();++si)
		out.push_back(*si);
}

template<class Tp,class Tp2>
double	FindSmallestDistance(int &idx, std::vector<Tp> &vec, Tp2 &pt){
	int i,n=(int)vec.size();
	double d,min=1000000;
	idx=-1;
	for(i=0;i<n;i++){
		d=vec[i].Distance(pt);
		if(d<min){
			min=d;
			idx=i;
		}
	}
	return min;
}

template<class Tp,class Tp2>
double	FindSmallestDistance(int &idx, std::vector<Tp> &x, std::vector<Tp> &y, Tp2 &pt){
	int i,n=(int)x.size();
	double d,min=1000000;
	idx=-1;
	for(i=0;i<n;i++){
		d=pt.Distance(x[i],y[i]);
		if(d<min){
			min=d;
			idx=i;
		}
	}
	return min;
}

template<class Tp,class Tp2>
double	FindSmallestDistance(int &i1, int &i2, std::vector<std::vector<Tp> > &vec, Tp2 &pt){
	int i,j,n=(int)vec.size(),ni;
	double d,min=1000000;
	i1=i2=-1;
	for(i=0;i<n;i++){
		ni=(int)vec[i].size();
		for(j=0;j<ni;j++){
			d=vec[i][j].Distance(pt);
			if(d<min){
				min=d;
				i1=i;
				i2=j;
			}
		}
	}
	return min;
}

template<class Tp,class Tp2>
double	FindBestWithMaxDist(int &idx, std::vector<Tp> &vec, Tp2 &pt,float maxDist){
	int i,n=(int)vec.size();
	double maxProb=0;
	idx=-1;
	double d;
	for(i=0;i<n;i++){
		d=vec[i].Distance(pt);
		if(d<maxDist && vec[i]._prob>maxProb){
			idx=i;
			maxProb=vec[i]._prob;
		}
	}
	return maxProb;
}


template<class Tp>
int FindLargest(std::vector<Tp> &in){
	int i,n=(int)in.size(),maxat=0;
	if (n==0)	return -1;
	double maxp=in[0]._prob;
	for (i=1;i<n;i++)
		if (in[i]._prob>maxp){
			maxat=i;
			maxp=in[i]._prob;
		}
	return maxat;
}

template<class Tp>
int FindSmallest(std::vector<Tp> &in){
	int i,n=(int)in.size(),minat=0;
	if (n==0)	return -1;
	double minp=in[0]._err;
	for (i=1;i<n;i++)
		if (in[i]._err<minp){
			minat=i;
			minp=in[i]._err;
		}
	return minat;
}

template<class Tp>
void KeepLocalMax(std::vector<Tp> &out, std::vector<Tp> &in, int window, int nx, int ny){
	SimpleMatrix<double> mmax;
	int i,n=(int)in.size(),x,y;
	mmax.SetDimension(ny/window+2,nx/window+2);
	mmax.InitValue(0);
	n=(int)in.size();
	for (i=0;i<n;i++){
		x=(int)(in[i].x()/(float)window);y=(int)(in[i].y()/(float)window);
		if (in[i]._prob>mmax(y,x))
			mmax(y,x)=in[i]._prob;
	}
	for (i=0;i<n;i++){
		x=(int)(in[i].x()/(float)window);y=(int)(in[i].y()/(float)window);
		if (in[i]._prob>=mmax(y,x)-0.0000001)
			out.push_back(in[i]);
	}
}

// Finds the largest probability element from in 
// that is at distance at least distMin from away
// Tp is a list or a vector
template<class Tp, typename DistMeasure>
typename Tp::iterator FindBestAtDistance(Tp &in, Tp &away, DistMeasure dm, double distMin){
	typename Tp::iterator i,ie=in.end(),maxat=ie;
	double d,max=-10000;
	for (i=in.begin();i!=ie;++i){
		d=i->Prob();
		if (d>max&&MinValue(away,*i,dm)>=distMin){
			maxat=i;
			max=d;
		}
	}
	return maxat;
}

// keep the largest probability, then suppress the ones within dist from it
// then keep the largest probability remaining, and so on ...
template<class Tp, typename DistMeasure>
void NonMaxSuppression(Tp &out, Tp &in, DistMeasure dm, double dist,int nmax, float thr=0){
	int i;
	Tp tmp;
	typename Tp::iterator j;
	tmp=in;
	out.clear();
	for (i=0;i<nmax;i++){
		j=FindBestAtDistance(tmp,out,dm,dist);
		if (j!=tmp.end()&&j->Prob()>thr){
			out.push_back(*j);
			j->Prob()=thr;
		}
		else
			break;
	}
}

template<class Tp>
void RemoveClose(std::vector<Tp> &out, const std::vector<Tp> &in, Tp &cand, double dist){
	int i,n=(int)in.size();
	out.clear();
	for (i=0;i<n;i++){
		if (cand.Distance(in[i])>=dist)
			out.push_back(in[i]);
	}
}

template<class Tp,class Tp2>
double	FindClosest(int &idx, const std::vector<Tp> &vec, Tp2 &pt){
	int i,n=(int)vec.size();
	double d,min=1000000;
	idx=-1;
	for(i=0;i<n;i++){
		d=vec[i].Distance(pt);
		if(d<min){
			min=d;
			idx=i;
		}
	}
	return min;
}

template<class Tp,class Tp2>
double	FindDistance(const std::vector<Tp> &vec, Tp2 &pt){
	int i,n=(int)vec.size();
	double d,min=1000000;
	for(i=0;i<n;i++){
		d=vec[i].Distance(pt);
		if(d<min)
			min=d;
	}
	return min;
}

template<class Tp>
int FindBestAtDistance2(std::vector<Tp> &in, std::vector<Tp> &away, double dist){
	int i,n=(int)in.size();
	double max=-1000;
	int maxat=-1;
	for (i=0;i<n;i++){
		if (in[i]._prob>max&&FindDistance(away,in[i])>=dist){
			maxat=i;
			max=in[i]._prob;
		}
	}
	return maxat;
}

template<class Tp>
void NonMaxSuppression2(std::vector<Tp> &out, std::vector<Tp> &in, double dist,int nmax){
	int i,j,n=(int)in.size();
	std::vector<Tp> segs;
	segs=in;
	out.clear();
	for (i=0;i<nmax;i++){
		j=FindBestAtDistance2(segs,out,dist);
		if (j>=0&&segs[j]._prob>-1000){
			out.push_back(segs[j]);
			segs[j]._prob=-1000;
		}
		else
			break;
	}
}

template<class Tp>
void NonMaxSuppression3(std::vector<Tp> &out, const std::vector<Tp> &in, double dist,int nmax){
	int i,j,n=(int)in.size(),cur;
	std::vector<Tp> tmp[2];
	cur=0;tmp[cur]=in;
	out.clear();
	for (i=0;i<nmax;i++){
		j=FindSmallest(tmp[cur]);
		if (j<0)
			break;
		Tp pt=tmp[cur][j];
		out.push_back(pt);
		RemoveClose(tmp[1-cur],tmp[cur],pt,dist);
		cur=1-cur;
	}
}

template<class Tp>
void GetAllWithName(std::vector<Tp> &out, std::string &name, std::vector<Tp> &vsampl){
	int i,n=(int) vsampl.size();
	for (i=0;i<n;i++){
		if (vsampl[i]._name==name){
			out.push_back(vsampl[i]);
		}
	}
}

template<class Tp>
void GetAllWithNameAndFrameNo(std::vector<Tp> &out, std::string &name, int frameNo, std::vector<Tp> &vsampl){
	int i,n=vsampl.size();
	for (i=0;i<n;i++){
		if (vsampl[i]._name==name&&vsampl[i]._frameNo==frameNo){
			out.push_back(vsampl[i]);
		}
	}
}

template<class Tp>
bool Thomas( std::vector<Tp> &a, std::vector<Tp> &b, std::vector<Tp> &c, std::vector<Tp> &x ) {
	unsigned long i, n = (unsigned long) x.size();
	Tp tmp;

	if ( b[0] == 0 )
		return true;

	c[0] /= b[0];
	x[0] /= b[0];

	for ( i = 1; i < n; ++i ) {
		tmp = b[i]-c[i-1]*a[i];
		if ( tmp == 0 ) 
			return true;
		c[i] /= tmp;
		x[i] = (x[i]-x[i-1]*a[i])/tmp;
	}

	for ( i = n-1; i > 0; --i ) {
		x[i-1] = x[i-1]-c[i-1]*x[i];
	}

	return false;
}

   
template<typename Func>
int Bisection( Func &func, double x[3], int steps, double tol ) {
    double y[3];
    int i;
    if ( x[0] >= x[2] )
		return -1;
    y[0] = func(x[0]);
    y[2] = func(x[2]);
    if ( y[0] == 0 ) {
        x[1] = x[0];
        return 0;
    }
    if ( y[2] == 0 ) {
        x[1] = x[2];
        return 0;
    }
    for ( i = 0; i < steps; ++i ) {
		x[1] = 0.5*(x[0]+x[2]);
		y[1] = func(x[1]);
		if ( 0.5*(x[2]-x[0]) <= tol || y[1] == 0 )
			return i;
		if ( y[0]*y[1] < 0 ) {
			x[2] = x[1];
			y[2] = y[1];
		}
		else if ( y[1]*y[2] < 0 ) {
			x[0] = x[1];
			y[0] = y[1];
		}
		else
			return -1;
    }
    return -1;
}

template<class Tp>
void Set1Minus2(std::vector<Tp> &out,std::vector<Tp> &s1,std::vector<Tp> &s2){
	std::set<Tp> s2s;
	typename std::vector<Tp>::iterator i,te;
	typename std::set<Tp>::iterator se;
	te=s2.end();
	for (i=s2.begin();i!=te;++i)
		s2s.insert(*i);
	out.clear();out.reserve(s1.size());
	te=s1.end();se=s2s.end();
	for (i=s1.begin();i!=te;++i)
		if (s2s.find(*i)==se)
			out.push_back(*i);
}

template<class Tp>
void Intersect(std::vector<Tp> &out,std::vector<Tp> &s1,std::vector<Tp> &s2){
	std::vector<Tp> s1s,s2s,tmp;
	typename std::vector<Tp>::iterator i,te;
	s1s=s1;
	s2s=s2;
	std::sort(s1s.begin(),s1s.end());
	std::sort(s2s.begin(),s2s.end());
	std::set_intersection(s1s.begin(),s1s.end(),s2s.begin(),s2s.end(),std::back_inserter(tmp));
	te=std::unique(tmp.begin(),tmp.end());
	out.clear();out.reserve(tmp.size());
	for (i=tmp.begin();i!=te;++i)
		out.push_back(*i);
}

template<class Tp>
void MergeSets(std::vector<Tp> &out,std::vector<Tp> &s1,std::vector<Tp> &s2){
	std::vector<Tp> s1s,s2s,tmp;
	typename std::vector<Tp>::iterator i,te;
	s1s=s1;
	s2s=s2;
	std::sort(s1s.begin(),s1s.end());
	std::sort(s2s.begin(),s2s.end());
	tmp.resize(s1.size()+s2.size());
	std::merge(s1s.begin(),s1s.end(),s2s.begin(),s2s.end(),tmp.begin());
	te=std::unique(tmp.begin(),tmp.end());
	out.clear();out.reserve(tmp.size());
	for (i=tmp.begin();i!=te;++i)
		out.push_back(*i);
}

template<class Tp>
void MergeSetsSVM(std::vector<Tp> &out,std::vector<Tp> &s1,std::vector<Tp> &s2){
	std::vector<Tp> s1s,s2s,tmp;
	typename std::vector<Tp>::iterator i,te;
	s1s=s1;
	s2s=s2;
	std::sort(s1s.begin(),s1s.end());
	std::sort(s2s.begin(),s2s.end());
	tmp.resize(s1.size()+s2.size());
	std::merge(s1s.begin(),s1s.end(),s2s.begin(),s2s.end(),tmp.begin());
	te=std::unique(tmp.begin(),tmp.end());
	out.clear();out.reserve(tmp.size());
	for (i=tmp.begin();i!=te;++i)
		out.push_back(*i);
}

template<class Tp>
bool PutIntoVectorI(std::vector<Tp> &out, const char *str, const char *dlm){
	// for integer-like Tp
	char *tmp, *p, *tok;
	out.clear();
	if ( str==NULL ) 
		return false;
	tmp = new char[strlen(str)+1];
	strcpy( tmp, str );
	for ( p = tmp; tok = strtok(p,dlm); p = NULL )
//		if (strlen(tok)>0)
			out.push_back((Tp)atoi(tok));
	delete [] tmp;
	return true;
}

template<class Tp>
bool PutIntoVectorF(std::vector<Tp> &out, const char *str, const char *dlm){
	// for float-like Tp
	char *tmp, *p, *tok;
	out.clear();
	if ( str==NULL ) 
		return false;
	tmp = new char[strlen(str)+1];
	strcpy( tmp, str );
	for ( p = tmp; tok = strtok(p,dlm); p = NULL )
//		if (strlen(tok)>0)
			out.push_back((Tp)atof(tok));
	delete [] tmp;
	return true;
}

template<class Tp,class TpY>
bool ReadSvm(std::vector<std::vector<Tp>> &x, std::vector<TpY> &y, const char *name, const char *dlm){
	char line[100000];
	std::vector<std::string> v,v2;
	int nVar=0;
	FILE *f=fopen(name,"rt");
	if (f==0)
		return false;
	while(!feof(f)){
		std::vector<Tp> tmp;
		tmp.reserve(1000);
		tmp.assign(nVar,0);
		if (fgets(line, 100000, f)==0)
			break;
		PutIntoVector(v, line,dlm);
		for (int i=1;i<(int)v.size();i++){
			PutIntoVector(v2, v[i].c_str(),":");
			int idx=atoi(v2[0].c_str());
			Tp val=(Tp)atof(v2[1].c_str());
			while (idx>=tmp.size())
				tmp.push_back(0);
			tmp[idx]=val;
		}
		y.push_back((TpY)atof(v[0].c_str()));
		x.push_back(tmp);
		nVar=std::max((int)tmp.size(),nVar);
	}
	fclose(f);
	return true;
}

template<class Tp,class TpY>
bool ReadSvm(std::vector<std::vector<std::pair<int,Tp>>> &x, std::vector<TpY> &y, const char *name, const char *dlm){
	char line[100000];
	std::vector<std::string> v,v2;
	FILE *f=fopen(name,"rt");
	if (f==0)
		return false;
	while(!feof(f)){
		std::vector<std::pair<int,Tp>> tmp;
		tmp.reserve(1000);
		if (fgets(line, 100000, f)==0)
			break;
		PutIntoVector(v, line,dlm);
		for (int i=1;i<(int)v.size();i++){
			PutIntoVector(v2, v[i].c_str(),":");
			int idx=atoi(v2[0].c_str());
			Tp val=(Tp)atof(v2[1].c_str());
			tmp.push_back(std::pair<int,Tp>(idx,val));
		}
		y.push_back((TpY)atof(v[0].c_str()));
		x.push_back(tmp);
	}
	fclose(f);
	return true;
}


#endif
