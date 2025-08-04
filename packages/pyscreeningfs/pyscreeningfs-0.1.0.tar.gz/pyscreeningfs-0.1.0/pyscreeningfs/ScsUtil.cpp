#include "ScsUtil.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cassert>
#include <cstdarg>
#include <cctype>
#include <ctime>

#ifdef _MSC_VER
// Specific to Visual Studio
//#include <hash_map>
#include <unordered_map>
#endif // _MSC_VER

using namespace std;

//! Global log file for training.
char fnGlobalLogfile[261] = "printf.txt";

std::string GetCurrentTimeString() {
  char a_cTimeBuf[128] = "";
  time_t tTime = 0;

  time(&tTime);

// NOTE: We need to do this in a thread-safe portable way (ctime() is NOT thread safe)

#ifdef _WIN32
  ctime_s(a_cTimeBuf, sizeof(a_cTimeBuf), &tTime);
#else // !_WIN32
  // NOTE: FreeBSD man page says that the character buffer should be at least 26 characters
  ctime_r(&tTime, a_cTimeBuf);
#endif // _WIN32

  return std::string(a_cTimeBuf);
}

int64_t Rand64() {
  // NOTE: Should use C++11 random features in the future
  // XXX: This may not actually be uniform!!!

#ifdef _WIN32
  // Windows is dumb. It only supports 15 bit random numbers from rand()
  return (int64_t)rand() |
        ((int64_t)rand() << 15) |
        ((int64_t)rand() << 30) |
        ((int64_t)rand() << 45);
#else // !_WIN32
  // Every other OS at least returns 31 bit random numbers
  return (int64_t)rand() |
        ((int64_t)rand() << 31);
#endif // _WIN32
}

double AUC(std::vector<float> &det, std::vector<float> &fp){
	// area under the ROC curve
	double sum=0,df,md;
	int n=(int)det.size();
	for (int i=0;i<n;i++){
		if (i==0){
			df=1-fp[i];
			md=(1+det[i])*0.5f;			
		}else if (i==n-1){
			df=fp[i];
			md=det[i]*0.5f;
		}else{
			df=fp[i]-fp[i-1];
			md=(det[i]+det[i-1])*0.5f;
		}
		sum+=df*md;
	}
	return -sum;
}

void ConsumeWhiteSpace(FILE *pFile) {
  int c;
  while ((c = fgetc(pFile)) != EOF && std::isspace(c)) { }

  if (c != EOF)
    ungetc(c, pFile);
}

#ifdef _MSC_VER
void FindSameLabel(std::vector<std::vector<int> > &qids, std::vector<std::string> &label){
	std::unordered_map<std::string,std::vector<int> > hm;
	std::unordered_map<std::string,std::vector<int> >::iterator hi,he;

	int nobs=(int)label.size();
	for (int i=0;i<nobs;i++){
		hi=hm.find(label[i]);
		if (hi!=hm.end()){
			hi->second.push_back(i);
		}
		else{
			std::vector<int> v(1);
			v[0]=i;
			hm.insert(std::unordered_map<std::string,std::vector<int> >::value_type(label[i],v));
		}
	}
	qids.clear();
	for (hi=hm.begin();hi!=hm.end();++hi)
		qids.push_back(hi->second);
}

void FindPairsSameLabel(std::vector<std::pair<int,int> > &pairs, std::vector<int> &label){
	std::unordered_map<int,std::vector<int> > hm;
	std::unordered_map<int,std::vector<int> >::iterator hi,he;

	int nobs=(int)label.size();
	for (int i=0;i<nobs;i++){
		hi=hm.find(label[i]);
		if (hi!=hm.end()){
			hi->second.push_back(i);
		}
		else{
			std::vector<int> v(1);
			v[0]=i;
			hm.insert(std::unordered_map<int,std::vector<int> >::value_type(label[i],v));
		}
	}
	pairs.clear();
	he=hm.end();
	for (hi=hm.begin();hi!=he;++hi){
		std::vector<int> &v=hi->second;
		int i,j,n=(int)v.size();
		for (i=0;i<n;i++)
		for (j=i+1;j<n;j++)
			pairs.push_back(std::pair<int,int>(v[i],v[j]));
	}
}
#else // !_MSC_VER
#warning "FindSameLabel and FindPairsSameLabel are unavailable."
#endif  // _MSC_VER

double RSquare(int nObs, double sumy, double sumyy, double sumdd){
	double meany=sumy/nObs;
	double vary=sumyy/nObs-meany*meany;
	return 1-sumdd/nObs/vary;
}

void AppendAndAdd(vector<string> &pos, const char *str1, const char *str2, float perc){
	srand(0);
	vector<string> tmp;
	int n=(int)pos.size(),na;
	SubSample(tmp,pos,perc);
	na=(int)tmp.size();
	pos.resize(n+na);
	for (int i=0;i<n;i++)
		pos[i].append(str1);
	for (int i=0;i<na;i++){
		pos[i+n]=tmp[i];
		pos[i+n].append(str2);
	}
}

void AppendAndDuplicate(vector<string> &pos, const char *str1, const char *str2){
	vector<string> tmp=pos;
	int n=(int)pos.size();
	pos.resize(2*n);
	for (int i=0;i<n;i++){
		pos[i].append(str1);
		pos[i+n]=tmp[i];
		pos[i+n].append(str2);
	}
}

int TestVars(vector<int> &sel, const set<int> &strue){
	// return how many of the elements of sel are found
	int i,kstar=(int)strue.size(),n=(int)sel.size(),nfound=0;
	for (i=0;i<n;i++){
		if (strue.find(sel[i])!=strue.end())
			nfound++;
	}
	return nfound;
}

int TestVars(vector<int> &cumsum, vector<int> &sel, const set<int> &strue){
	// return how many of the elements of sel are found
	int i,j,kstar=(int)strue.size(),n=(int)sel.size();
	vector<int> det;
	set<int>::iterator si,se=strue.end();
	det.assign(n,0);
	for (si=strue.begin();si!=se;++si){
		j=*si;
		i=FindElement(sel,j);
		if (i>=0){
			det[i]=1;
		}
	}
	int nfound=Sum(det);
	CumSum(cumsum,det);
	return nfound;
}

void CreateCrossValFold(vector<int> &train, vector<int> &test, int nObs, int nFolds, int iFold){
	train.clear();
	test.clear();
	train.reserve(nObs);
	test.reserve(nObs/nFolds+1);
	for (int i=0;i<nObs;i++){
		int j=i%nFolds;
		if (j==iFold)
			test.push_back(i);
		else
			train.push_back(i);
	}
}

bool CreateCrossValFolds(char *filenames, int nfolds){
	int i,n,j;
	char st[2550],dirName[2550],st1[100];

	std::vector<string> names,tmp;
	std::vector<vector<string> > foldnames;
	vector<int> perm;

	SplitPathFileNameExtension(dirName,st,st1,filenames);
	if (!ReadLines(names,filenames)){
		cout << filenames<< "not found.\n";
		return false;
	}
	cout << "Creating crossvalidation file lists.\n";
	n=(int)names.size();
	srand((unsigned int) time(0));
	Choose(perm,n,n);

	foldnames.resize(nfolds);
	for (i=0;i<n;i++){
		j=i%nfolds;
		foldnames[j].push_back(names[perm[i]]);
	}

	for (i=0;i<nfolds;i++){
		sprintf(st,"%s/xval%d_test_%d.txt",dirName,nfolds,i);
		SaveLines(st,foldnames[i]);
	}
	for (i=0;i<nfolds;i++){
		tmp.clear();
		for (j=0;j<nfolds;j++){
			if(j!=i)
				AppendToVector(tmp,foldnames[j]);
		}
		sprintf(st,"%s/xval%d_train_%d.txt",dirName,nfolds,i);
		SaveLines(st,tmp);
	}
	return true;
}


int Sign( int n ){ 
	if( n > 0 )
		return 1;
	else if( n < 0 )
		return -1;
	else
		return 0;
}

double Sigmoid(double x){
	return  1./(1.+exp(-x));
}

int RandInt(int n){
	//random integer btw 0 and n-1
	int k=(int)(n*(rand()/(RAND_MAX+1.)));
	if (k>n-1)
		k=n-1;
	return k;
}

double RandDbl(double d){
	//random double btw 0 and d
	return (rand()*d)/(RAND_MAX+1.);
}

void SampleBernoulli(std::vector<int> &out, int n, double prob){
	double thr=(double(RAND_MAX)+1)*prob;
	out.assign(n,0);
	for (int i=0;i<n;i++){
		if (rand()<=thr)
			out[i]=1;
	}
}

void SampleBernoulliIdx(std::vector<int> &out, int n, double prob){
	double thr=(double(RAND_MAX)+1)*prob;
	out.clear();
	out.reserve(n);
	for (int i=0;i<n;i++){
		if (rand()<=thr)
			out.push_back(i);
	}
}

int Round(float x) { 
	return static_cast<int>(x + x > 0.0 ? +0.5 : -0.5); 
}

double NormRand(){
	static int next_gaussian = 0;
	static double saved_gaussian_value;

	double fac, rsq, v1, v2;

	if (next_gaussian == 0) {
		do {
			v1 = 2.0*RandDbl(1)-1.0;
			v2 = 2.0*RandDbl(1)-1.0;
			rsq = v1*v1+v2*v2;
		} while (rsq >= 1.0 || rsq == 0.0);
		fac = sqrt(-2.0*log(rsq)/rsq);
		saved_gaussian_value=v1*fac;
		next_gaussian=1;
		return v2*fac;
	}
	else{
		next_gaussian=0;
		return saved_gaussian_value;
	}
}

int IntClose(double x){
	double y1 = (double)ceil(x);
	double y2 = (double)floor(x);
	if (fabs(y1-x)<fabs(y2-x))
		return (int)y1;
	else
		return (int)y2;
}

bool KeepNumbersOnly(const char *fnout, const char *fnin){
	FILE	*pfile,*f;
	char	str_temp[100001];
	
	pfile = fopen(fnin, "rt");
	f = fopen(fnout, "wt");
	if (pfile == 0||f==0)
		return false;
	
	long counter = 0; // for debugging
	while (!feof(pfile)){
		counter++;
		if (fgets(str_temp, 100000, pfile)==0)
			break;
		vector<float> v;
		PutIntoVector(v,str_temp," ");
		if (v.size()>1&&v[1]!=0){
			fprintf(f,"%s",str_temp);
		}
	}
	fprintf(f,"\n");
	fclose(pfile);
	fclose(f);
	return true;
}

void KeepFilenameOnly(std::vector<std::string> &out, std::vector<std::string> &in){
	char path[1000],fn[255];
	string s;
	out.resize(in.size());
	for (int i=0;i<(int)in.size();i++){
		strcpy(fn,in[i].c_str());
		GetLastWord(path, fn, '/', true);
		if (strlen(path) == 0)
			GetLastWord(path, fn, '\\', true);
		out[i]=fn;
	}
}

void Choose(vector<int> &idx, int n,int k){ 
	// Sample k random numbers w/o replacement from 0...n-1 and put them in idx
	// Ref: Knuth, D. E., The Art of Computer Programming, Vol. 2:
	// Seminumerical Algorithms. London: Addison-Wesley, 1969.
	int i,j,tmp; 
	vector<int> v;
	v.resize(n);
	idx.resize(k);
	for (i=0;i<n;i++)
		v[i]=i;
	for (i=0;i<k;i++){
		j=RandInt(n-i);
		idx[i]=v[j];
		tmp=v[n-i-1];	//swap v[j] with v[n-i-1]
		v[n-i-1]=v[j];
		v[j]=tmp;
	}
}

void ChooseSplit(vector<int> &idx, vector<int> &v, int k){ 
	// Sample k random numbers w/o replacement from v, put them in idx and remove them from v
	// Ref: Knuth, D. E., The Art of Computer Programming, Vol. 2:
	// Seminumerical Algorithms. London: Addison-Wesley, 1969.
	int i,j,tmp,n=(int)v.size(); 
	idx.resize(k);
	for (i=0;i<k;i++){
		j=RandInt(n-i);
		idx[i]=v[j];
		tmp=v[n-i-1];	//swap v[j] with v[n-i-1]
		v[n-i-1]=v[j];
		v[j]=tmp;
	}
	for (i=0;i<k;i++)
		v.pop_back();
}

bool InBounds(int rows,int cols, int i, int j){
	if ((i<0 )||(j<0)||(i>=rows)||(j>=cols)) 
		return false;
	else
		return true;
}

double	BhattacharyyaDistance(std::vector<double> &p, std::vector<double> &q){
	double sum=0;
	int i,n=(int)p.size();
	for (i=0;i<n;i++)
		sum+=sqrt(p[i]*q[i]);
	return sum;
}

float EqualErrorRate(std::vector<float> &det, std::vector<float> &fa){
	// assumes det is decreasing
	int i,n=(int)det.size();
	for (i=0;i<n;i++){
		if (det[i]<1-fa[i])
			break;
	}
	float d1=1-det[i-1],d2=1-det[i];
	float f1=fa[i-1],f2=fa[i];
	return (f1*d2-d1*f2)/(d2-d1-f2+f1);
}

float	EqualErrorRate(std::vector<float> *roc){
	return EqualErrorRate(roc[0],roc[1]);
}

float Entropy(std::vector<float> &prob){
	float sum=0;
	int i,n=(int)prob.size();
	for (i=0;i<n;i++){
        if(prob[i]>0)
			sum += prob[i]*log(prob[i]);
	}
	return -sum;
}

bool ReadLinePoints(vector<Pointf> &pts,char * name){
	vector<float> tmp;
	FILE *f=fopen(name,"rt");
	if(f==0)
		return false;
	if (LineRead(tmp,f,",",100000)){
		fclose(f);
		int n=(int)tmp.size()/2;
		pts.resize(n);
		for (int i=0;i<n;i++)
			pts[i].Set(tmp[2*i],tmp[2*i+1]);
		return true;
	}
	return false;
}

bool ReadPoints(vector<Pointf> &pts,char *filename){
	FILE *f=fopen(filename,"rt");
	if (f==0)
		return false;
	int i,n;
	float x,y;
	fscanf(f,"%d\n",&n);
	pts.resize(n);
	for (i=0;i<n;i++){
		fscanf(f,"%f %f\n",&x,&y);
		pts[i].Set(x,y);
	}
	return true;
}

bool ReadAsf(vector<Pointf> &pts, const char *name){
	// extension does not have to be correct
	char line[1000],st[255];
	int n=0;
	strcpy(line,name);
	GetFirstField(st,line,'.');
	sprintf(line,"%s.asf",st);
	FILE *pfile=fopen(line,"rt");
	Pointf p;
	if (pfile==0)
		return false;
	pts.clear();
	while (!feof(pfile)){
		if (fgets(line, 1000, pfile)==0)
			break;
		if (line[0]=='#'||strlen(line)==0||line[0]==10)
			continue;
		if (n==0){
			n=atoi(line);
		}
		else{
			vector<float> vf;
			PutIntoVector(vf,line,"\t");
			p.Set(vf[2],vf[3]);
			pts.push_back(p);
			if (pts.size()==n)
				break;
		}
	}

	fclose(pfile);
	return true;
}

bool ReadMod(vector<Pointf> &pts, const char *name){
	// extension does not have to be correct
	char line[1000],st[255];
	int n=0,np,k,l;
	float x,y;
	strcpy(line,name);
	GetFirstField(st,line,'.');
	sprintf(line,"%s.mod",st);
	FILE *pfile=fopen(line,"rt");
	Pointf p;
	if (pfile==0)
		return false;
	pts.clear();
	fgets(line, 1000, pfile);
	fgets(line, 1000, pfile);
	sscanf(line,"FeatureNum=%d",&n);
	for (int i=0;i<n;i++){
		fgets(line, 1000, pfile);
		fgets(line, 1000, pfile);
		if (fgets(line, 1000, pfile)==0)
			break;
		sscanf(line,"PointNum=%d",&np);
		for (int j=0;j<np;j++){
			if (fgets(line, 1000, pfile)==0)
				break;
			sscanf(line,"%d %d %f %f",&k,&l,&x,&y);
			p.Set(x,y);
			pts.push_back(p);
		}
	}

	fclose(pfile);
	return true;
}

bool Log2File(char *filename, const char * format, ...){
	FILE *f=fopen(filename,"a+");
	if (f!=NULL){
		va_list arguments;
		va_start(arguments, format);
		int result = vfprintf(f,format, arguments);
		va_end(arguments);
		fclose(f);
		return true;
	}
	return false;
}

bool PrintOut(std::vector<float> &values, char *fmt, char sep){
	return Log2File(fnGlobalLogfile,values,fmt,sep);
}

void PrintOut(const char * format, ...){
	FILE *pfile;
	pfile = fopen(fnGlobalLogfile, "at");
	if (pfile != NULL){
		va_list arguments;
		va_start(arguments, format);
		vfprintf(pfile,format, arguments);
		va_end(arguments);
		fclose(pfile);
	}
}

void FindFirstName(char *name, char *root, char *ext){ 
	FILE *f=0;
	int n=0;
	do{
		n++;
		sprintf(name,"%s%02d.%s",root,n,ext);
		if (f!=0)
			fclose(f);
		f=fopen(name,"rb"); 
	}while(f!=0);
	if (f!=0)
		fclose(f);
}

void DlmWrite(FILE *f,const SimpleMatrix<int> &M, char dlm){
	int r=M.rows(),c=M.cols();
	for(int i=0;i<r;i++){
		for(int j=0;j<c-1;j++)
			fprintf(f,"%d%c",M.Data(i,j),dlm);
		fprintf(f,"%d\n",M.Data(i,c-1));
	}
}

void DlmWrite(FILE *f, const SimpleMatrix<double> &M, char dlm){
	int r=M.rows(),c=M.cols();
	for(int i=0;i<r;i++){
		for(int j=0;j<c-1;j++)
			fprintf(f,"%1.6f%c",M.Data(i,j),dlm);
		fprintf(f,"%1.6f\n",M.Data(i,c-1));
	}
}

bool SaveToFile(char *name, vector<Pointf> &pts){
	vector<float> tmp;
	int n=(int)pts.size();
	if (n==0)
		return true;
	tmp.resize(n*2);
	for (int i=0;i<n;i++){
		tmp[2*i]=pts[i].x();
		tmp[2*i+1]=pts[i].y();
	}
	return DlmWrite(name,tmp,"%1.1f",',');
}

//bool DlmReadn(FILE *f, SimpleMatrix<int> &M, char dlm){
//	int r=M.rows(),c=M.cols();
//	std::vector<string> vstrings;
//	char *line=new char[c*10];
//	for(int i=0;i<r;i++){
//		if (fgets(line, c*10, f)==0)
//			break;
//		PutIntoStringVector(vstrings, line,dlm);
//		if((int)vstrings.size()<c){
//			delete []line;
//			return false;
//		}
//		for(int j=0;j<c;j++)
//			M(i,j)=atoi(vstrings[j].c_str());
//	}
//	delete []line;
//	return true;
//}

void LineSkip(FILE *f){
	char line[10000];
	fgets(line, 10000, f);		
}

void CutHeadBlank(char * lpszDest, char * lpszSour){
	char * lpszMove;
	if(lpszDest == NULL || lpszSour == NULL)
		return;
	lpszMove = lpszSour;
	while(strlen(lpszMove) > 0 && lpszMove[0] == ' ')
		lpszMove ++;
	strcpy(lpszDest, lpszMove);
}

void CutEndBlank(char * lpszDest, char * lpszSour){
	if(lpszDest == NULL || lpszSour == NULL)
		return;
	strcpy(lpszDest, lpszSour);
	//Delete balnk at the end of string
	while(strlen(lpszDest) >0 && lpszDest[strlen(lpszDest) - 1] == ' ')
		lpszDest[strlen(lpszDest) - 1] = '\0';
}

void CutBlank(char * lpszDest, char * lpszSour){
	if(lpszDest == NULL || lpszSour == NULL)
		return;
	CutEndBlank(lpszDest, lpszSour);
	CutHeadBlank(lpszDest, lpszDest);
}

void GetFirstWord(char *str_dest, char *str_sour){
	int	nfrom=-1,nto=-1,nlen,i;
	
	nlen = (int)strlen(str_sour);
	i = 0;
	while (nfrom<0 && i<nlen){
		if (str_sour[i] != ' ' && str_sour[i] != 9 && str_sour[i] != ';')
			nfrom = i;
		i++;
	}
	if (nfrom >= 0){
		while (nto<0 && i<nlen){
			if (str_sour[i] == ' ' || str_sour[i] == 9 || str_sour[i] == ';')
				nto = i-1;
			i++;
		}
		if (nto < 0)
			nto = nlen-1;

		for (i=nfrom; i<=nto; i++)
			str_dest[i-nfrom] = str_sour[i];
		str_dest[nto-nfrom+1] = '\0';
		for (i=nto+1; i<=nlen; i++)
			str_sour[i-(nto+1)] = str_sour[i];
		str_sour[nlen-(nto+1)] = '\0';
	}
	else
		str_dest[0] = '\0';
}

void GetFirstWord(char * lpszDest, char * lpszSour, char cSeprator, bool bChangeSour){
	char  *pBuf, *pSearch;
	if (strlen(lpszSour) > 0 && lpszDest != NULL){
		pBuf = new char[strlen(lpszSour) + 1];
		strcpy(pBuf, lpszSour);
		pSearch = strchr(pBuf, cSeprator);
		if (pSearch != NULL){
			pSearch[0] = '\0';	//Found this character
			if(bChangeSour)
				strcpy(lpszSour, pSearch + 1);
		}
		else
			pBuf[0] = '\0';		//Didn't find this character
		CutBlank(pBuf, pBuf);
		strcpy(lpszDest, pBuf);
		delete []pBuf;
	}
}

void GetLastWord(char * lpszDest, char * lpszSour, char cSeprator, bool bChangeSour){
	char  *pBuf, *pSearch;
	if (strlen(lpszSour) > 0 && lpszDest != NULL){
		pBuf = new char[strlen(lpszSour) + 1];
		strcpy(pBuf, lpszSour);
		pSearch = strrchr(pBuf, cSeprator);
		if (pSearch != NULL){
			pSearch[0] = '\0';	//Found this character
			if(bChangeSour)
				strcpy(lpszSour, pSearch + 1);
		}
		else
			pBuf[0] = '\0';		//Didn't find this character
		CutBlank(pBuf, pBuf);
		strcpy(lpszDest, pBuf);
		delete []pBuf;
	}
}

void GetFirstField(char *str_dest, char *str_sour, char dlm){
	int	nfrom=-1,nto=-1,nlen,i;
	
	nlen = (int)strlen(str_sour);
	i = 0;
	while (nfrom<0 && i<nlen){
		if (str_sour[i] != dlm)
			nfrom = i;
		i++;
	}
	if (nfrom >= 0){
		while (nto<0 && i<nlen){
			if (str_sour[i] == dlm)
				nto = i-1;
			i++;
		}
		if (nto < 0)
			nto = nlen-1;

		for (i=nfrom; i<=nto; i++)
			str_dest[i-nfrom] = str_sour[i];
		str_dest[nto-nfrom+1] = '\0';
		for (i=nto+1; i<=nlen; i++)
			str_sour[i-(nto+1)] = str_sour[i];
		str_sour[nlen-(nto+1)] = '\0';
	}
	else
		str_dest[0] = '\0';
}

// Used for the Hopkins Dataset
bool PutIntoVector(std::vector<double> &out, int* label_init, char *str_sour, const char dlm) {
	out.clear();
	
	if (str_sour==NULL)
		return false;
	int i,l=(int)strlen(str_sour);
	if (l<=0)
		return false;
	char	*pbegin;
	double	val;

	bool flag = false;
	
	pbegin=str_sour;
	for (i=0;i<l;i++){
		if (str_sour[i] == dlm){
			str_sour[i]=0;
			val=atof(pbegin);
			if(flag) {
				out.push_back(val);
			}
			else {
				*label_init = (int)val;
				flag = true;
			}
				str_sour[i]= dlm;
				pbegin=&str_sour[i+1];
		}
	}
	val=atof(pbegin);
	out.push_back(val);
	l=(int)out.size();
	return true;
}

void PutIntoVector(std::vector<string> &vstrings, const char *str, const char *dlm ) {
	char *tmp, *p, *tok;
	vstrings.clear();

	if ( str==NULL ) return;

	tmp = new char[strlen(str)+1];
	strcpy( tmp, str );

	for ( p = tmp; tok = strtok(p,dlm); p = NULL )
//		if (strlen(tok)>0)
			vstrings.push_back(tok);

	delete [] tmp;
}

void CopyFile(const char *to, const char *from){
	ifstream source(from, ios::binary);
    ofstream dest(to, ios::binary);

    istreambuf_iterator<char> begin_source(source);
    istreambuf_iterator<char> end_source;
    ostreambuf_iterator<char> begin_dest(dest); 
    copy(begin_source, end_source, begin_dest);

    source.close();
    dest.close();
}

void ClearFile(const char * filename){
	FILE *f=fopen(filename,"w");
	if (f!=NULL){
		fclose(f);
	}
}

/* --------------------------------------------------------------------------- */
/* ****************************** CountLines() ***************************** */
/* --------------------------------------------------------------------------- */
/*  > Input Arguments:
	1. const char *filename - this function will count the number of lines in the 
	file 'filename'

	-----------------------------------------------------------------------------
	< Output:
	Number of lines (if any).
*/
int	CountLines(const char *filename){
	FILE *f=fopen(filename,"rt");
	char str_temp[100000];
	int n=0;
	if (f==0)
		return -1;
	while (!feof(f)){
		if (fgets(str_temp, 100000, f)==0)
			break;
		if (!feof(f))
			n++;
	}
	fclose(f);
	return n;
}

void GetFileNameOnly(char * lpszDest, const char * lpszSour){
	char *p_buf1,*p_buf2;

	p_buf1 = new char[strlen(lpszSour)+1];
	p_buf2 = new char[strlen(lpszSour)+1];

	strcpy(p_buf2, lpszSour);

	GetLastWord(p_buf1, p_buf2, '.');
	if (strlen(p_buf1) == 0)
		strcpy(p_buf1, p_buf2);
	GetLastWord(p_buf2, p_buf1, '/', true);
	if (strlen(p_buf2) == 0)
		GetLastWord(p_buf2, p_buf1, '\\', true);
	strcpy(lpszDest, p_buf1);
	delete []p_buf1;
	delete []p_buf2;
}

void GetFileNameWithExtensionOnly(char * lpszDest, const char * lpszSour){
	char *p_buf1,*p_buf2, *ext;

	p_buf2 = new char[strlen(lpszSour)+1];
	ext = new char[strlen(lpszSour)+1];
	p_buf1 = new char[strlen(lpszSour)+1];
	SplitPathFileNameExtension(p_buf2,p_buf1,ext, lpszSour);
/*
	strcpy(p_buf2, lpszSour);
	strcpy(ext, lpszSour);

	GetLastWord(p_buf1, ext, '.',true);
	if (strlen(p_buf1) == 0)
		strcpy(p_buf1, p_buf2);
	GetLastWord(p_buf2, p_buf1, '/', true);
	if (strlen(p_buf2) == 0)
		GetLastWord(p_buf2, p_buf1, '\\', true);
	*/
	sprintf(lpszDest,"%s.%s", p_buf1,ext);
	delete []p_buf1;
	delete []ext;
	delete []p_buf2;
}

void RenameExtension(char *path, char *ext){
	char tmp[255],filename[2550];
	strcpy(tmp,path);
	GetLastWord(filename,tmp,  '.',true);
	if (strlen(filename) == 0){
		strcpy(filename, path);
		strcpy(tmp,"");
	}
	sprintf(path,"%s%s",filename,ext);
}

void SplitPathFileNameExtension(char *path, char *filename,char *ext, const char * lpszSour){
	strcpy(path, lpszSour);
	strcpy(ext, lpszSour);
	GetLastWord(filename, ext, '.',true);
	if (strlen(filename) == 0){
		strcpy(filename, path);
		strcpy(ext,"");
	}
	GetLastWord(path, filename, '/', true);
	if (strlen(path) == 0)
		GetLastWord(path, filename, '\\', true);
}

bool StringEndsCaseInsensitive(const char * string, const char * ending){
  if (ending == 0||string == 0) return false;
  long string_length = (int)strlen(string);
  long ending_length = (int)strlen(ending);
  if (ending_length > string_length) return false;
#ifdef _WIN32
  long result = _stricmp(&(string[string_length - ending_length]), ending);
#else 
  long result = strcasecmp(&(string[string_length - ending_length]), ending);
#endif 
  return (result == 0);
}

bool StripLinesTok( char *fout, char *fin, const char *dlm){
	// remove lines and replace the dlm with cr-lf
	FILE	*pfile,*f;
	char	str_temp[100001],str1[100000],all[300000];
	string  str;
	
	pfile = fopen(fin, "rt");
	if (pfile == NULL)
		return false;
	f = fopen(fout, "wt");
	if (f == NULL)
		return false;
	
	long counter = 0; // for debugging
	strcpy(all,"");
	while (!feof(pfile)){
		counter++;
		if (fgets(str_temp, 100000, pfile)==0)
			break;
		GetFirstField(str1, str_temp, '\n');
		if (str1 != NULL){
			strcat(all,str1);
		}
	}
	fclose(pfile);
	char *p,*tok;
	for ( p = all; tok = strtok(p,dlm); p = NULL )
			fprintf(f,"%s\n",tok);	
	fclose(f);
	return true;
}

/* ****** bool SaveLines(const char *file, std::vector<std::string> &vsampl) ******
This function writing to the file ...
	
	--------------------------------------------------------------------------------------------------------
	> Input
	  1] const char *file - 
	  2] std::vector<std::string> &vsampl - 
*/
bool SaveLines(const char *file, std::vector<std::string> &vsampl, int saveEol){
	FILE	*pfile;
	int n=(int)vsampl.size();
	pfile = fopen(file, "wt");
	if (pfile == NULL)
		return false;
	if (saveEol)
		for (int i=0;i<n;i++)
			fprintf(pfile,"%s\n",vsampl[i].c_str());
	else
		for (int i=0;i<n;i++)
			fprintf(pfile,"%s",vsampl[i].c_str());
	fclose(pfile);
	return true;
}

bool AddLines(const char *fnDest, const char *fnSrc){
	// Add to fnDest the lines from the fnSrc
	FILE	*pfile,*fout;
	char	str_temp[100001];
	string  str;
	
	pfile = fopen(fnSrc, "rt");
	if (pfile == NULL){
		printf("%s not found \n",fnSrc);
		return false;
	}
	fout = fopen(fnDest, "a+t");
	if (fout == NULL){
		printf("%s not found \n",fnDest);
		fclose(pfile);
		return false;
	}
	
	long counter = 0; // for debugging
	while (!feof(pfile)){
		counter++;
		if (fgets(str_temp, 100000, pfile)==0)
			break;
		fputs(str_temp,fout);
	}

	fclose(pfile);
	fclose(fout);
	return true;
}

bool ReadLines(std::vector<string> &vsampl, const char *file, int maxNo){
	FILE	*pfile;
	char	str_temp[100001],str1[100000];
	string  str;
	
	pfile = fopen(file, "rt");
	if (pfile == NULL)
		return false;
	
	long counter = 0; // for debugging
	while (!feof(pfile)){
		counter++;
		if (fgets(str_temp, 100000, pfile)==0)
			break;
		GetFirstField(str1, str_temp, '\n');
		if (str1 != NULL){
			str = str1;
			vsampl.push_back(str);
			if (maxNo>0&&counter>=maxNo)
				break;
		}
	}

	fclose(pfile);
	return true;
}

bool ReadLines(std::vector<string> &vsampl, const char *file, float subSampleProb){
	FILE	*pfile;
	char	str_temp[100001],str1[100000];
	string  str;
	
	pfile = fopen(file, "rt");
	if (pfile == NULL)
		return false;
	
	long counter = 0; // for debugging
	while (!feof(pfile)){
		counter++;
		if (fgets(str_temp, 100000, pfile)==0)
			break;
		GetFirstField(str1, str_temp, '\n');
		if (str1 != NULL&&RandDbl(1)<subSampleProb){
			str = str1;
			vsampl.push_back(str);
		}
	}

	fclose(pfile);
	return true;
}

// Line format: string int
bool ReadLines(const char* filename, std::vector<std::string> &vsampl, std::vector<int>& num) {
	assert(filename != NULL);

	vsampl.clear();
	num.clear();

	char str_temp[1000001];

	std::ifstream pfile(filename);
	if (!pfile) {
		std::cout << "Read data from '" << filename << "' failed!\n";
		return false;
	}

	while (pfile.good()) {
		pfile.getline(str_temp,1000001);

		std::string a;
		int b;
		
		std::istringstream ist(str_temp);
		ist >> a >> b;
		
		vsampl.push_back(a);
		if(!ist.fail()) {
			num.push_back(b);
		}
	}

	pfile.close();
    
	return true;
}

// Line format: string int
// characters after '#' will be ignored
/* *** ReadLines() ***
*/
bool ReadLines(const char* filename, std::vector<std::string> &vsampl) {
	//check that the filename is not empty
	assert(filename != NULL);

	vsampl.clear();

	std::ifstream pfile(filename);
	if (!pfile) {
		std::cout << "Read data from '" << filename << "' failed!\n";
		return false;
	}

	std::string str_temp;
	while (std::getline(pfile, str_temp)) {
		size_t found = str_temp.find_first_of("#", 0);
		std::string a;
		
		if(found != std::string::npos)
			a = str_temp.substr(0, found);
		else
			a = str_temp;

		if(a.length() > 0) {
			int i = 0;
			while((a[i] == ' ' || a[i] == '\t') && a.length() > 0)
				a.erase(0, 1);
		}

		if(a.length() > 0) {
			size_t i = a.length() - 1;
			while((a[i] == ' ' || a[i] == '\t') && a.length() > 0) {
				a.erase(a.begin() + i);
				i--;
			}
		}
		
		if(a.length() != 0 && a.compare("\0") != 0 && a.compare("\n") != 0)
			vsampl.push_back(a);
	}

	pfile.close();
    
	return true;
}

/* --------------------------------------------------------------------------- */
/* ******************************* SubSample() ******************************* */
/* --------------------------------------------------------------------------- */
/*  > Input Arguments:
	1. char *fileOut - will write the sampled examples to the file in 'fileOut'
	2. char *fileIn - file from which this function will sample
	3. double prob - will determine what percent is sampled

	-----------------------------------------------------------------------------
	< Output:
	A boolean value of 'true' if successful sampling was performed, otherwise, 
	'false' is returned.

*/
bool SubSample(char *fileOut, char *fileIn, double prob){
	char str_temp[100000];
	printf("Subsampling %s at %g rate\n",fileIn, prob);
	FILE *f=fopen(fileIn,"rt");
	if (f==0)
		return false;
	FILE *out=fopen(fileOut,"wt");
	if (out==0){
		fclose(f);
		return false;
	}
	while (!feof(f)){
		if (fgets(str_temp, 100000, f)==0)		
			break;
		// the function 'RandDbl(d)' returns a random double between
		// 0 and d.
		if (!feof(f)&&RandDbl(1)<prob)
			fputs(str_temp,out);
			
	}
	fclose(f);
	fclose(out);
	return true;
}

bool Permute(int *v, std::vector<int> &result, const int start, const int n){  
	if (start >= n || v == nullptr)
		return false;

	if (start == n-1) {
		for (int i = 0; i < n; i++) {
			result.push_back(v[i]);
		}
    }
    else {
		for (int i = start; i < n; i++) {
			int tmp = v[i];
      
			v[i] = v[start];
		    v[start] = tmp;
			Permute(v, result, start+1, n);
			v[start] = v[i];
			v[i] = tmp;
		}
	}

	return true;
}
