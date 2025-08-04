#ifndef _POINT_H
#define _POINT_H
#pragma warning(disable:4786)

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif

#include <vector>
#include <functional>
#include <cmath>
#include <iostream>
#include <fstream>
#include <math.h>

template<class Tp>
class Point{
	template<class fTp>
	friend std::ostream & operator<<( std::ostream &os, const Point<fTp> &p );
	template<class fTp>
	friend std::istream & operator>>( std::istream &is, Point<fTp> &p );
public:
	Tp _x;
	Tp _y; 
	Point(){_x=0;_y=0;};
	Point(Tp x1,Tp y1){_x=x1;_y=y1;};
	template<class Tp2>
	Point(Point<Tp2> &p){_x=(Tp)p._x;_y=(Tp)p._y;}

	void operator>>(std::ofstream &strm){
		strm.write((char*)&_x, sizeof(_x));
		strm.write((char*)&_y, sizeof(_y));
	}

	void operator<<(std::ifstream &strm){
		strm.read((char*)&_x, sizeof(_x));
		strm.read((char*)&_y, sizeof(_y));
	}
	virtual	void operator>>(FILE &strm){
		fwrite(&_x, sizeof(_x), 1, &strm);
		fwrite(&_y, sizeof(_y), 1, &strm);
	}
	virtual	void operator<<(FILE &strm){
		fread(&_x, sizeof(_x), 1, &strm);
		fread(&_y, sizeof(_y), 1, &strm);
	}
	template<class Tp2>
	Point<Tp> & operator=(const Point<Tp2> &p){
		if(this!=(Point<Tp> *)&p){
			_x=(Tp)p._x;_y=(Tp)p._y;
		}
		return *this;
	}
	template<class Tp2>
	inline operator Point<Tp2>(){
		Point<Tp2> P;P._x=(Tp2)_x;P._y=(Tp2)_y;
		return P;
	}
	bool operator==(const Point& p)const{
		return ((_x==p._x)&&(_y==p._y));
	}
	bool operator!=(const Point& p){
		return ((_x!=p._x)||(_y!=p._y));
	}
	bool EqualInt(const Point& p){
		return ((int)_x==(int)p.x()&&(int)_y==(int)p.y());
	}
	bool lessY(const Point& p){ 
		if (_y<p._y) return true;
		if (_y>p._y) return false;
		return (_x<p._x);
	}
	template<class Tp2>
	bool less(const Point<Tp2>& p){ 
		if (_x<p._x) return true;
		if (_x>p._x) return false;
		return (_y<p._y);
	}
	template<class Tp2>
	bool operator<(const Point<Tp2>& p){ 
		return less(p);
	}
	Point operator+(const Point& p){
		Point q;q._x=_x+p._x;q._y=_y+p._y;
		return q;
	};
	Point operator-(const Point& p){
		Point q;q._x=_x-p._x;q._y=_y-p._y;
		return q;
	};
	Point operator*(double d) const{
		Point q;q._x= (Tp) (_x*d);q._y= (Tp) (_y*d);
		return q;
	};
	Point operator/(double d) const{
		Point q;q._x= (Tp) (_x/d);q._y= (Tp) (_y/d);
		return q;
	}
	Point operator+=(const Point& p){
		_x+=p._x;_y+=p._y;
		return *this;
	}
	Point operator-=(const Point& p){
		_x-=p._x;_y-=p._y;
		return *this;
	}
	Point operator*=(const Point& p){
		_x*=p._x;_y*=p._y;
		return *this;
	}
	Point operator*=(const Tp d){
		_x*=d;_y*=d;
		return *this;
	}
	Point operator/=(const Tp d){
		_x/=d;_y/=d;
		return *this;
	}

    // ACCESS
	Tp X() const {return _x;}
	Tp Y() const {return _y;}
	Tp x() const {return _x;}
	Tp y() const {return _y;}
	Tp &x() {return _x;}
	Tp &y() {return _y;}
	Tp GetX() {return _x;}
	Tp GetY() {return _y;}
  	Tp& rX(){return _x;}
	Tp& rY(){return _y;}
	void SetX(const Tp x1){_x=x1;}
	void SetY(const Tp y1){_y=y1;}
    void Set(const Tp x1, const Tp y1){_x=x1;_y=y1;}
    void Get(Tp& x1, Tp& y1){x1=_x;y1=_y;}
	inline	Tp	Row(void) const {return _x;};
	inline	Tp	Col(void) const {return _y;};
	inline  void	SetRow(const Tp row1){_x=row1;};
	inline	void	SetCol(const Tp col1){_y=col1;};
	void	Set(const Point &pt){
		_x=pt._x;_y=pt._y;
	}

	void	SetRound(const Point &pt){
		double temp1,temp2;
		temp1 = ceil((double)pt.X());
		temp2 = floor(pt.X());
		if (fabs(pt.X()-temp1) < fabs(pt.X()-temp2))
			_x = (Tp) temp1;
		else
			_x = (Tp) temp2;
		temp1 = ceil((double)pt.Y());
		temp2 = floor(pt.Y());
		if (fabs(pt.Y()-temp1) < fabs(pt.Y()-temp2))
			_y = (Tp) temp1;
		else
			_y = (Tp) temp2;
	}
    // OPERATIONS 
	void Scale(Tp scale){_x *= scale;_y *= scale;}
	double SqDistance(double x1, double y1) const{	
		double dx = _x-x1;
		double dy = _y-y1;
		return dx * dx + dy * dy;
	}
	double SqDistance(const Point& p) const{	
		return SqDistance(p._x,p._y);
	}
	double Distance(double x1, double y1) const{	
		double dx = _x-x1;
		double dy = _y-y1;
		double s = dx * dx + dy * dy;
		return (double)sqrt(s);
	}
	template<class Tp2>
	double Distance(const Point<Tp2>& p) const{	
		return Distance((double)p._x,(double)p._y);
	}
	double NormL1(const Point& p){	//norm 1
		double dx = p._x-_x;
		double dy = p._y-_y;
		return fabs(dx)+fabs(dy);
	}
	double NormInfty(const Point& p){	//norm infinity
		double dx = fabs(p._x-_x);
		double dy = fabs(p._y-_y);
		if (dx>dy)
			return dx;
		return dy;
	}
	double Azimuth(double x1, double y1){return (double)atan2(y1-_y,x1-_x);} 
	double Azimuth(const Point& p){return (double)atan2(p._y-_y,p._x-_x);} 
	double	Norm(){return sqrt((double)_x*_x+_y*_y);}//distance to zero
	void	Normalize(){(*this)/=(Tp)Norm();}
	double SumSq(){return _x*_x+_y*_y;}
	void print(){std::cout << _x << ',' << _y << std::endl;}
	void SaveToLine(char *buff){
		double xd=_x,yd=_y;
		sprintf(buff,"%2.3f,%2.3f",xd,yd);
	}
	bool Bound(int nx,int ny){
		bool b;
		if (_x<0){
			_x=0;
			b=false;
		}
		if (_x>nx-1){
			_x=nx-1;
			b=false;
		}
		if (_y<0){
			_y=0;
			b=false;
		}
		if (_y>ny-1){
			_y=ny-1;
			b=false;
		}
		return b;
	}
	void Zero(){_x=0;_y=0;}

	struct LexOrder : public std::binary_function<Point<Tp>,Point<Tp>, bool> {
		bool operator()(const Point<Tp> &p, const Point<Tp>  &q) const {
			if (p._x<q._x) return true;
			if (p._x>q._x) return false;
			return (p._y<q._y);
		}
	};
	struct xOrder : public std::binary_function<Point<Tp>,Point<Tp>, bool> {
		bool operator()(const Point<Tp> &p, const Point<Tp>  &q) const {
			return p._x<q._x;
		}
	};
	struct yOrder : public std::binary_function<Point<Tp>,Point<Tp>, bool> {
		bool operator()(const Point<Tp> &p, const Point<Tp>  &q) const {
			return p._y<q._y;
		}
	};
	struct yOrderInv : public std::binary_function<Point<Tp>,Point<Tp>, bool> {
		bool operator()(const Point<Tp> &p, const Point<Tp>  &q) const {
			return p._y>q._y;
		}
	};
};


typedef Point<float>	Pointf;
typedef Point<double>	Pointd;
typedef Point<int>		Pointi;
typedef Point<double>	McPoint2D;
typedef Point<long>		McImagePoint;
typedef std::vector<Pointi> PointList;

template<class fTp>
std::ostream & operator<<( std::ostream &os, const Point<fTp> &p ) {
	os << p._x << '\t' << p._y;
	return os;
}

template<class fTp>
std::istream & operator>>( std::istream &is, Point<fTp> &p ) {
	is >> p._x >> p._y;
	return is;
}

inline double DistPointf(Point<float> &p, Point<float> &q){return p.Distance(q);}

template<class Tp>
double	GetAngle(Point<Tp> &P0, Point<Tp> &P1, Point<Tp> &P2){
	//returns angle btw 0 and 2PI in couterclockwise direction
	//to rotate P0P1 to get it over P2P1
	double a1=atan2((double)P0._y-P1._y,(double)P0._x-P1._x);
	double a2=atan2((double)P2._y-P1._y,(double)P2._x-P1._x);
	double a=a2-a1;
	if (a<0)
		a=a+2*M_PI;
	return a;
}
template<class Tp>
double	GetAngle(Point<Tp> &P0, Point<Tp> &P1, Point<Tp> &P2, Point<Tp> &P3){
	Point<Tp> P=P1+P3-P2;
	return GetAngle(P0,P1,P);
}

template<class Tp>
inline double AvgPtDist(std::vector<Tp> &pts0, std::vector<Tp> &pts){
	double sum=0,d;
	int i,n=(int)pts.size();
//	vector<double> di(n);
	for (i=0;i<n;i++){
		d=pts[i].Distance(pts0[i]);
		sum+=d;
//		di[i]=d;
	}
	return sum/n;
}

inline double AvgSqDist(std::vector<Point<float> > &pts0, std::vector<Point<float> > &pts){
	double sum=0;
	int i,n=(int)pts.size();
	for (i=0;i<n;i++)
		sum+=pts[i].SqDistance(pts0[i]);
	return sum/n;
}

template<class Tp>
struct yOrder : public std::binary_function<Point<Tp>,Point<Tp>, bool> {
	bool operator()(const Point<Tp> &p, const Point<Tp>  &q) const {
		return p._y<q._y;
	}
};

template<class Tp>
bool operator<(const Point<Tp>& p,const Point<Tp>& q){ 
	if (p._x<q._x) return true;
	if (p._x>q._x) return false;
	return (p._y<q._y);
}

template <typename T>
inline Point<T> operator+(const Point<T>& lhs, const Point<T>& rhs)
{
  Point<T>       res(lhs);

  res += rhs;
  return res;
}

template <typename T>
inline Point<T> operator-(const Point<T>& lhs, const Point<T>& rhs)
{
  Point<T>       res(lhs);

  res -= rhs;
  return res;
}

template <typename T>
inline T operator*(const Point<T>& lhs, const Point<T>& rhs){
	// dot product 
	return lhs.x()*rhs.x()+lhs.y()*rhs.y();
}

template <typename T>
inline Point<T> operator*(const Point<T>& lhs, T rhs){
  Point<T>       res(lhs);
  res *= rhs;
  return res;
}

template <typename T>
inline bool LexOrderStartAt(int l, const std::vector<Point<T> > &x,const std::vector<Point<T> > &y){
	if (l<x.size()-1&&x[l]==y[l]){
		return LexOrderStartAt(l+1,x,y);
	}
	if (l<x.size())
		return x[l]<y[l];
	else
		return false;
}

#endif
