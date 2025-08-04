#ifndef _SIMPLE_MATRIX_H
#define _SIMPLE_MATRIX_H

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif

#include <vector>
#include <cassert>
#include <cmath>
#include <iostream>
#include "VectorUtil.h"

//#define PI	3.1415926535897931

typedef double* pdouble;
typedef unsigned char uchar;

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
template<class Tp>
class SimpleMatrix:public std::vector<Tp>{
public:
		SimpleMatrix();
		SimpleMatrix( int row, int col);
		SimpleMatrix(const SimpleMatrix& x);
        ~SimpleMatrix();
		void Init(const SimpleMatrix& x);
		
		//OPERATORS
		SimpleMatrix<Tp>&	operator=(const SimpleMatrix<Tp>& x );

		Tp&				operator()(const int row, const int col);
		const Tp&       operator()(const int row, const int col) const;
		Tp&				Data(const int row, const int col) const;
		bool			Valid(const int row, const int col) const;
		bool			Valid(const int row) const;
		void			GetPos(const long index, long &j, long &i);
		void			SetCopy(const Tp * pData, int nRows, int nCols);
		void			SetDimension(const int row, const int col=0);
		template<class Tp2>
		void			SetDimension(const SimpleMatrix<Tp2> &M){SetDimension(M.ny(),M.nx());}
		void			CopyRow(std::vector<Tp> &out, int line);
		void			CopyCol(std::vector<Tp> &out, int col);
		void			GetDimension(int& row, int& col) const; 
		Tp *			GetData(){return &this->at(0);}
		Tp *			GetData(int row) const{return _pDataIdx[row];}
		long			rows() const{return _nRow;};
		long			cols() const{return _nCol;};
		int				nx() const{return _nCol;};
		int				ny() const{return _nRow;};
		SimpleMatrix	T() const;
		SimpleMatrix	Rotate90(int K) const;

		inline	void	InitValue(Tp value);
		void			Clear(){std::vector<Tp>::clear();_pDataIdx.clear();_nRow=_nCol=0;}

	#define DEFOP(OP) \
		SimpleMatrix<int> operator OP (const Tp val); 
		DEFOP(>)
		DEFOP(>=)
		DEFOP(<)
		DEFOP(<=)
		DEFOP(==)
		DEFOP(!=)
	#undef DEFOP				
protected:
		void	UpdateIdx();

public:
		std::vector<Tp *>	_pDataIdx;
		int		_nRow, _nCol;
};

template<class Tp, class Tp2>
void CopyData(SimpleMatrix<Tp> &to, Tp2 *v2, int nrows, int ncols){
	Tp2 *ptr=v2;
	to.SetDimension(nrows,ncols);
	for(int i=0;i<nrows;i++){
	for (int j=0;j<ncols;j++){
			to(i,j)=(Tp)(*ptr);
			++ptr;
		}
	}
}

template<class Tp, class Tp2>
void CopyDataT(SimpleMatrix<Tp> &to, Tp2 *v2, int nrows, int ncols){
	Tp2 *ptr=v2;
	to.SetDimension(nrows,ncols);
	for (int j=0;j<ncols;j++){
		for(int i=0;i<nrows;i++){
			to(i,j)=(Tp)(*ptr);
			++ptr;
		}
	}
}

template<class Tp>
void CopyMatrixu(SimpleMatrix<unsigned char> &Mu,SimpleMatrix<Tp> &M){
	size_t i,n=M.size();
	int f;
	Mu.SetDimension(M.rows(),M.cols());
	for(i=0;i<n;i++){
		f=(int) (M[i]);
		if (f<0) f=0;
		if (f>255) f=255;
		Mu[i]=(unsigned char)(f);
	}
}

template<class Tp>
void CopyMatrixu(SimpleMatrix<unsigned char> &Mu,std::vector<std::vector<Tp>> &v){
	int y,x;
	int f,ny=(int)v.size(),nx=(int)v[0].size();
	Mu.SetDimension(ny,nx);
	for(y=0;y<ny;y++)
	for(x=0;x<nx;x++){
		f=(int) (v[y][x]);
		if (f<0) f=0;
		if (f>255) f=255;
		Mu(y,x)=(unsigned char)(f);
	}
}

template<class Tp, class Tp2>
void CopyMatrix(SimpleMatrix<Tp> &out,SimpleMatrix<Tp2> &M){
	size_t i,n=M.size();
	out.SetDimension(M.rows(),M.cols());
	for(i=0;i<n;i++)
		out[i]=(Tp)M[i];
}

template<class Tp>
void Crop(SimpleMatrix<Tp> &out,SimpleMatrix<Tp> &M, int x0, int y0, int nx, int ny){
	// crop patch of size ny x nx with left top corner at x0,y0
	int x1=x0+nx,y1=y0+ny;
	out.SetDimension(ny,nx);
	for(int y=y0;y<y1;y++)
	for (int x=x0;x<x1;x++)
		if (M.Valid(y,x))
			out(y-y0,x-x0)=M(y,x);
		else
			out(y-y0,x-x0)=0;
}

template<class Tp1, class Tp2>
void CopyMatrix(SimpleMatrix<Tp1>& mx_dest,const SimpleMatrix<Tp2>& mx_src){
	mx_dest.SetDimension(mx_src.rows(), mx_src.cols());
	size_t i, n=mx_src.size();
	for(i = 0; i < n; i++)
		mx_dest[i] = (Tp1)(mx_src[i]);
}

template<class Tp1, class Tp2>
void CopyMatrix(std::vector<std::vector<Tp1>>& mx_dest,const SimpleMatrix<Tp2>& mx_src){
	int nr=mx_src.rows(),nc=mx_src.cols();
	mx_dest.resize(nr);
	for(int i = 0; i < nr; i++){
		std::vector<Tp1> &x=mx_dest[i];
		x.resize(nc);
		for (int j=0;j<nc;j++)
			x[j] = (Tp1)(mx_src(i,j));
	}
}

template<class Tp>
SimpleMatrix<Tp>::SimpleMatrix(){  //null matrix
	_nRow	= 0;
	_nCol	= 0;
}

template<class Tp>
SimpleMatrix<Tp>::SimpleMatrix(int row, int col){	
	_nRow	= 0;
	_nCol	= 0;
	SetDimension(row,col);
}

template<class Tp>
SimpleMatrix<Tp>::SimpleMatrix(const SimpleMatrix& x){//copy constructor
	Init(x);
}

template<class Tp>
SimpleMatrix<Tp>::~SimpleMatrix(){  //delete the m_pdata
//	MatrixFree(); //free the memory
}

template<class Tp>
void SimpleMatrix<Tp>::SetDimension(const int row, const int col){  
	//set the dimension and allocates the memory of the matrix
	if (row!=_nRow || col!=_nCol){
		_nRow = row;
		_nCol = col;
#ifdef _DEBUG
	assert(_nRow >= 0);
	assert(_nCol >= 0);
#endif
		this->resize(((long)row) * col);
		UpdateIdx();
	}
}

template<class Tp>
void SimpleMatrix<Tp>::Init(const SimpleMatrix& x){
	*(std::vector<Tp> *)this=x;
	_nRow = x._nRow; _nCol = x._nCol;
	UpdateIdx();
}

template<class Tp>
void SimpleMatrix<Tp>::UpdateIdx(){
	_pDataIdx.resize(_nRow);
	for (long i=0; i<_nRow; i++)
		_pDataIdx[i] = &this->at(_nCol*i);
}

template<class Tp>
void SimpleMatrix<Tp>::SetCopy(const Tp * pData, int nRows, int nCols){
	SetDimension(nRows,nCols);
	memcpy( &this->at(0), pData, this->size() * sizeof(Tp) );
}

template<class Tp>
Tp& SimpleMatrix<Tp>::operator ()(const int row, const int col){
#ifdef _DEBUG
	assert(row < _nRow && row >= 0);
	assert(col < _nCol && col >= 0);
#endif
	return _pDataIdx[row][col];
}

template<class Tp>
const Tp& SimpleMatrix<Tp>::operator ()(const int row, const int col) const {
#ifdef _DEBUG
	assert(row < _nRow && row >= 0);
	assert(col < _nCol && col >= 0);
#endif
	return _pDataIdx[row][col];
 }

template<class Tp>
SimpleMatrix<Tp>& SimpleMatrix<Tp>::operator=(const SimpleMatrix<Tp>& x){
	//performs assignment statement

	if ( this != &x ){
		*(std::vector<Tp> *)this=x;
		_nRow = x._nRow; _nCol = x._nCol;
		UpdateIdx();
	}
	return *this;
}

#define DEFOP(OP)					\
template<class Tp>					\
SimpleMatrix<int> SimpleMatrix<Tp>::operator OP (const Tp b) {	\
	SimpleMatrix<int> c (this->rows(), this->cols());	\
	size_t i, n=this->size();			\
        for (i = 0; i < n; i++) {			\
		c[i] = (int) (this->at(i) OP b);	\
	}						\
	return c;					\
} 
DEFOP(>)
DEFOP(>=)
DEFOP(<)
DEFOP(<=)
DEFOP(==)
DEFOP(!=)
#undef DEFOP

template<class Tp>
void SimpleMatrix<Tp>::GetPos(const long index, long &j, long &i)
{
	j = index/(cols());
	i = index-j*cols();
}

template<class Tp>
bool	SimpleMatrix<Tp>::Valid(const int row, const int col) const{
	if (row>=0 && row<rows() && col>=0 && col<cols())
		return true;
	else
		return false;
}

template<class Tp>
bool	SimpleMatrix<Tp>::Valid(const int row) const{
	if (row>=0 && row < this->size())
		return true;
	else
		return false;
}

template<class Tp>
Tp& SimpleMatrix<Tp>::Data(const int row, const int col) const{
#ifdef _DEBUG
	assert(row < _nRow && row >= 0);
	assert(col < _nCol && col >= 0);
#endif
	return _pDataIdx[row][col];
}

template<class Tp>
void SimpleMatrix<Tp>::GetDimension(int& row, int& col) const{  
	//report the dimension of the matrix
	 row = _nRow;
	 col = _nCol;
}

template<class Tp>
void SimpleMatrix<Tp>::CopyRow(std::vector<Tp> &out, int line){
	int i,n=cols();
	out.resize(n);
	for (i=0;i<n;i++)
		out[i]=Data(line,i);
}

template<class Tp>
void SimpleMatrix<Tp>::CopyCol(std::vector<Tp> &out, int col){
	int i,n=rows();
	out.resize(n);
	for (i=0;i<n;i++)
		out[i]=Data(i,col);
}

template<class Tp>
SimpleMatrix<Tp> SimpleMatrix<Tp>::T() const{
	//transposes of a matrix
	SimpleMatrix<Tp> temp;
	temp.SetDimension(_nCol, _nRow); //initialize a temp matrix
	for (int i = 0; i < _nCol; i++)
		for (int j = 0; j < _nRow; j++)
			temp(i, j) = Data(j, i); //transpose elements

	return temp;
}

template<class Tp>
SimpleMatrix<Tp> SimpleMatrix<Tp>::Rotate90(int K) const{
//	  ROT90  Rotate SimpleMatrix 90 degrees.
//    ROT90() is the 90 degree counterclockwise rotation of SimpleMatrix A.
//    ROT90(K) is the K*90 degree rotation of A, K = +-1,+-2,...
 
//    Example,
//        A = [1 2 3      B = rot90(A) = [ 3 6
//             4 5 6 ]                     2 5
//                                         1 4 ]
	int i,j;
	SimpleMatrix temp; //intialize a temp SimpleMatrix
    int k = K%4;
    if (k < 0)
        k += 4;
	switch (k){
	case 1:
		temp.SetDimension(_nCol,_nRow);
		for (i = 0; i < _nCol; i++)
			for (j = 0; j < _nRow; j++)
				temp(i, j) = Data(j, _nCol-i-1); //rotate elements
		 return temp;
	case 2:
		temp.SetDimension(_nRow,_nCol);
		for (i = 0; i <_nRow ; i++)
			for (j = 0; j < _nCol; j++)
				temp(i, j) = Data(_nRow-i-1, _nCol-j-1); //rotate elements
		 return temp;
	case 3:
		temp.SetDimension(_nCol,_nRow);
		for (i = 0; i < _nCol; i++)
			for (j = 0; j < _nRow; j++)
				temp(i, j) = Data(_nRow-j-1, i); //rotate elements

		 return temp;
	default:
		temp.SetDimension(_nRow,_nCol);
		for (i = 0; i <_nRow ; i++)
			for (j = 0; j < _nCol; j++)
				temp(i, j) = Data(i, j); 
		return temp;	
	}
}

template<class Tp>
void SimpleMatrix<Tp>::InitValue(Tp value){
	this->assign(((long)_nRow) * _nCol,value);
}

#endif
