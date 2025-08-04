/*
* Code Contributors
* Mingyuan Wang
* Built on top of Xgboost quantile structure. visit xgboost github for original code
*/

#ifndef QUANTILE_DRIFT_H_
#define QUANTILE_DRIFT_H_

#include <cmath>
#include <vector>
#include <cstring>
#include <algorithm>
#include <iostream>

namespace drift_summary {

	template<typename FType, typename DType, typename IType>
	struct WQSummary {
		/*! \brief an entry in the sketch summary */
		struct Entry {
			/*! \brief minimum rank */
			IType rmin;
			/*! \brief maximum rank */
			IType rmax;
			/*! \brief coverage */
			IType scov;
			/*! \brief maximum weight for label 1*/
			DType sweight0;
			/*! \brief maximum weight for label 0*/
			DType sweight1;
			/*! \brief the value of data */
			DType value;
			// constructor
			Entry() {}  // NOLINT
						// constructor
			Entry(IType rmin, IType rmax, IType scov, DType sweight0, DType sweight1, DType value)
				: rmin(rmin), rmax(rmax), scov(scov), sweight0(sweight0), sweight1(sweight1), value(value) {}
			/*!
			* \brief debug function,  check Valid
			* \param eps the tolerate level for violating the relation
			*/
			inline void CheckValid(FType eps = 0) const {
				CHECK(rmin >= 0 && rmax >= 0 && scov >= 0) << "nonneg constraint";
				CHECK(rmax - rmin - scov > -eps) << "relation constraint: min/max";
			}
			/*! \return rmin estimation for v strictly bigger than value */
			inline IType RMinNext() const {
				return rmin + scov;
			}
			/*! \return rmax estimation for v strictly smaller than value */
			inline IType RMaxPrev() const {
				return rmax - scov;
			}
		};
		/*! \brief input data queue before entering the summary */
		struct Queue {
			// entry in the queue
			struct QEntry {
				// value of the instance
				DType value;
				// coverage of instance
				IType cove;
				// weight of instance 1
				DType weight0;
				// weight of instance 0
				DType weight1;
				// value of the index
				IType qidx;
				// default constructor
				QEntry() = default;
				// constructor
				QEntry(DType value, IType cove, DType weight0, DType weight1, IType qidx)
					: value(value), cove(cove), weight0(weight0), weight1(weight1), qidx(qidx){}
				// comparator on value
				inline bool operator<(const QEntry &b) const {
					return value < b.value;
				}
			};
			// the input queue
			std::vector<QEntry> queue;
			// influence rate
			double _alpha, _beta;

			// end of the queue
			size_t qtail;
			// push data to the queue
			inline void Push(IType label, DType x, IType c) {
				int preidx = queue.size() - 1;
				if (qtail == 0 || queue[preidx].value != x) {
					if (label == 1) {
						queue.push_back(QEntry(x, c, 0.0, (double)_beta * c, qtail++));
					}
					else {
						queue.push_back(QEntry(x, c, (double)_beta * c, 0.0, qtail++));
					}
					//qtail++;
				}
				else {
					if (label == 1) {
						queue[preidx].weight1 = queue[preidx].weight1 * _alpha + (double)_beta * c;
						queue[preidx].weight0 = queue[preidx].weight0 * _alpha;
					}
					else {
						queue[preidx].weight0 = queue[preidx].weight0 * _alpha + (double)_beta * c;
						queue[preidx].weight1 = queue[preidx].weight1 * _alpha;
					}
					queue[preidx].cove += c;
					queue[preidx].qidx = qtail++;
				}
			}

			inline void PushSparse(IType label, DType x, IType c, DType w) {
				int preidx = queue.size() - 1;
				if (x != 0) {
					if (qtail == 0 || queue[preidx].value != x) {
						if (label == 1) {
							queue.push_back(QEntry(x, c, 0.0, (double)_beta * w, qtail++));
						}
						else {
							queue.push_back(QEntry(x, c, (double)_beta * w, 0.0, qtail++));
						}
					}
					else {
						if (label == 1) {
							queue[preidx].weight1 = queue[preidx].weight1 * _alpha + (double)_beta * w;
							queue[preidx].weight0 = queue[preidx].weight0 * _alpha;
						}
						else {
							queue[preidx].weight0 = queue[preidx].weight0 * _alpha + (double)_beta * w;
							queue[preidx].weight1 = queue[preidx].weight1 * _alpha;
						}
						queue[preidx].cove += c;
						qtail = qtail + c - 1;
						queue[preidx].qidx = qtail++;
					}
				}
				else {
					if (qtail == 0 || queue[preidx].value != x) {
						qtail = qtail + c - 1;
						if (label == 1) {
							queue.push_back(QEntry(x, c, 0.0, (double)w, qtail++));
						}
						else {
							queue.push_back(QEntry(x, c, (double)w, 0.0, qtail++));
						}
					}
					else {
						if (label == 1) {
							queue[preidx].weight1 = (double)w;
						}
						else {
							queue[preidx].weight0 = (double)w;
						}
						queue[preidx].cove += c;
						qtail = qtail + c - 1;
						queue[preidx].qidx = qtail++;
					}

				}
			}

			inline void MakeSummary(WQSummary *out) {
				std::sort(queue.begin(), queue.end());
				//out->size = 0;
				// start update sketch
				IType csum = 0;
				// construct data with unique weights
				for (size_t i = 0; i < queue.size();) {
					size_t j = i + 1;
					IType c = queue[i].cove; 
					DType w0 = exp(log(queue[i].weight0) + (qtail - queue[i].qidx - 1) * log(_alpha));
					DType w1 = exp(log(queue[i].weight1) + (qtail - queue[i].qidx - 1) * log(_alpha));
					while (j < queue.size() && queue[j].value == queue[i].value) {
						w0 += exp(log(queue[j].weight0) + (qtail - queue[j].qidx - 1) * log(_alpha));
						w1 += exp(log(queue[j].weight1) + (qtail - queue[j].qidx - 1) * log(_alpha));
						if (!(w0==w0) || !(w1 == w1)){//debug
							int check = 1;
						}
						c += queue[j].cove;
						++j; 
					}
					out->data.push_back(Entry(csum, csum + c, c, w0, w1, queue[i].value));
					//out->size++;
					csum += c; i = j;
				}
			}
		};
		/*! \brief data field */
		//Entry *data;
		std::vector<Entry> data;
		/*! \brief number of elements in the summary */
		//size_t size;
		// constructor
	/*		WQSummary(Entry *data, size_t size)
			: data(data), size(size) {}*/
		WQSummary(){}
		WQSummary(std::vector<Entry> &data)
			: data(data) {}
		/*!
		* \return the maximum error of the Summary
		*/
		inline IType MaxError() const {
			IType res = data[0].rmax - data[0].rmin - data[0].scov;
			for (size_t i = 1; i < data.size(); ++i) {
				res = std::max(data[i].RMaxPrev() - data[i - 1].RMinNext(), res);
				res = std::max(data[i].rmax - data[i].rmin - data[i].scov, res);
			}
			return res;
		}
		
		/*! \return maximum rank in the summary */
		inline IType MaxRank() const {
			return data.back().rmax;
		}
		/*!
		* \brief copy content from src
		* \param src source sketch
		*/
		inline void CopyFrom(const WQSummary &src) {
			//size = src.size;
			data=src.data;
		}
		inline void MakeFromSorted(const Entry* entries, size_t n) {
			//size = 0;
			for (size_t i = 0; i < n;) {
				size_t j = i + 1;
				// ignore repeated values
				for (; j < n && entries[j].value == entries[i].value; ++j) {}
				data.push_back(Entry(entries[i].rmin, entries[i].rmax, entries[i].scov, entries[i].sweight0, entries[i].sweight1,
					entries[i].value));
				//size++;
				i = j;
			}
		}
		/*!
		* \brief debug function, validate whether the summary
		*  run consistency check to check if it is a valid summary
		* \param eps the tolerate error level, used when IType is floating point and
		*        some inconsistency could occur due to rounding error
		*/
		inline void CheckValid(FType eps) const {
			for (size_t i = 0; i < data.size(); ++i) {
				data[i].CheckValid(eps);
				if (i != 0) {
					CHECK(data[i].rmin >= data[i - 1].rmin + data[i - 1].scov) << "rmin range constraint";
					CHECK(data[i].rmax >= data[i - 1].rmax + data[i].scov) << "rmax range constraint";
				}
			}
		}
		

		/*!
		* \brief set current summary to be merged summary of sa and sb
		* \param sa first input summary to be merged
		* \param sb second input summary to be merged
		*/
		inline void SetCombine(const WQSummary &sa,
			const WQSummary &sb) {
			if (sa.data.size() == 0) {
				this->CopyFrom(sb); return;
			}
			if (sb.data.size() == 0) {
				this->CopyFrom(sa); return;
			}
			//CHECK(sa.size > 0 && sb.size > 0);
			std::vector<Entry>::const_iterator a = sa.data.begin();
			std::vector<Entry>::const_iterator b = sb.data.begin();
			// extended rmin value
			IType aprev_rmin = 0, bprev_rmin = 0;
			//std::vector<Entry> dst = this->data;
			while (a != sa.data.end() && b != sb.data.end()) {
				// duplicated value entry
				if (a->value == b->value) {
					this->data.push_back(Entry(a->rmin + b->rmin,
						a->rmax + b->rmax,
						a->scov + b->scov, a->sweight0 + b->sweight0, a->sweight1 + b->sweight1, a->value));
					aprev_rmin = a->RMinNext();
					bprev_rmin = b->RMinNext();
					++a; ++b;
				}
				else if (a->value < b->value) {
					this->data.push_back(Entry(a->rmin + bprev_rmin,
						a->rmax + b->RMaxPrev(),
						a->scov, a->sweight0, a->sweight1, a->value));
					aprev_rmin = a->RMinNext();
					++a;
				}
				else {
					this->data.push_back(Entry(b->rmin + aprev_rmin,
						b->rmax + a->RMaxPrev(),
						b->scov, b->sweight0, b->sweight1, b->value));
					bprev_rmin = b->RMinNext();
					++b;
				}
			}
			//if (a->value == 820 && b->value==0) {
			//	++a;
			//	++a;
			//	++a;
			//	++a;
			//}
			if (a != sa.data.end()) {
				IType brmax = sb.data.rbegin()->rmax;
				do {
					this->data.push_back(Entry(a->rmin + bprev_rmin, a->rmax + brmax, a->scov, a->sweight0, a->sweight1, a->value));
					++a;
				} while (a != sa.data.end());
			}
			if (b != sb.data.end()) {
				IType armax = sa.data.rbegin()->rmax;
				do {
					this->data.push_back(Entry(b->rmin + aprev_rmin, b->rmax + armax, b->scov, b->sweight0, b->sweight1, b->value));
					++b;
				} while (b != sb.data.end());
			}
			//this->size = this->data.size() - data.size();
			const IType tol = 10;
			IType err_mingap, err_maxgap, err_wgap;
			this->FixError(&err_mingap, &err_maxgap, &err_wgap);
			if (err_mingap > tol || err_maxgap > tol || err_wgap > tol) {
				/*     LOG(INFO) */
				cout << "mingap=" << err_mingap
					<< ", maxgap=" << err_maxgap
					<< ", wgap=" << err_wgap;
			}
			//CHECK(size <= sa.size + sb.size) << "bug in combine";
		}
		
		// try to fix rounding error
		// and re-establish invariance
		inline void FixError(IType *err_mingap,	IType *err_maxgap,IType *err_wgap)  {
			*err_mingap = 0;
			*err_maxgap = 0;
			*err_wgap = 0;
			IType prev_rmin = 0, prev_rmax = 0;
			for (size_t i = 0; i < this->data.size(); ++i) {
				if (data[i].rmin < prev_rmin) {
					data[i].rmin = prev_rmin;
					*err_mingap = std::max(*err_mingap, prev_rmin - data[i].rmin);
				}
				else {
					prev_rmin = data[i].rmin;
				}
				if (data[i].rmax < prev_rmax) {
					data[i].rmax = prev_rmax;
					*err_maxgap = std::max(*err_maxgap, prev_rmax - data[i].rmax);
				}
				IType rmin_next = data[i].RMinNext();
				if (data[i].rmax < rmin_next) {
					data[i].rmax = rmin_next;
					*err_wgap = std::max(*err_wgap, data[i].rmax - rmin_next);
				}
				prev_rmax = data[i].rmax;
			}
		}
		
	};

	/*! \brief try to do efficient pruning */
	template<typename FType, typename DType, typename IType>
	struct WXQSummary : public WQSummary<FType, DType, IType> {
		// redefine entry type
		using Entry = typename WQSummary<FType, DType, IType>::Entry;
		// constructor
		WXQSummary() : WQSummary<FType, DType, IType>(){}
		WXQSummary(std::vector<Entry> &data)
			: WQSummary<FType, DType, IType>(data) {}
		// check if the block is large chunk
		inline static bool CheckLarge(const Entry &e, IType chunk) {
			return  e.RMinNext() > e.RMaxPrev() + chunk;
		}
		// set prune
		inline void SetPrune(const WQSummary<FType, DType, IType> &src, size_t maxsize) {
			if (src.data.size() <= maxsize) {
				this->CopyFrom(src); return;
			}
			IType begin = src.data[0].rmax;
			// n is number of points exclude the min/max points
			size_t n = maxsize - 2, nbig = 0;
			// these is the range of data exclude the min/max point
			IType range = src.data[src.data.size() - 1].rmin - begin;
			// prune off zero weights
			if (range == 0.0f || maxsize <= 2) {
				// special case, contain only two effective data pts
				if (1 < src.data.size() - 1) {
					Entry tempchunk = Entry(0, 0, 0, 0, 0, 0);
					IType dx2 = 2 * ((range) / n + begin);
					int h = 0;
					while (h < src.data.size() - 2 &&
						dx2 >= src.data[h + 1].rmax + src.data[h + 1].rmin) ++h;
					tempchunk.value = src.data[(int)ceil(h / 2)].value;
					tempchunk.rmin = src.data[0].rmin;
					tempchunk.rmax = src.data[h].rmax;
					for (int l = 0; l <= h; ++l) {
						tempchunk.scov += src.data[l].scov;
						tempchunk.sweight0 += src.data[l].sweight0;
						tempchunk.sweight1 += src.data[l].sweight1;
					}
					this->data.push_back(tempchunk);

					tempchunk = Entry(0, 0, 0, 0, 0, 0);
					tempchunk.value = src.data[(int)ceil((h + src.data.size()) / 2)].value;
					tempchunk.rmin = src.data[h + 1].rmin;
					tempchunk.rmax = src.data[src.data.size() - 1].rmax;
					for (int l = h + 1; l <= src.data.size() - 1; ++l) {
						tempchunk.scov += src.data[l].scov;
						tempchunk.sweight0 += src.data[l].sweight0;
						tempchunk.sweight1 += src.data[l].sweight1;
					}
					this->data.push_back(tempchunk);
				}
				else {
					this->data.push_back(src.data[0]);
					this->data.push_back(src.data[src.data.size() - 1]);
				}
				//this->size = 2;
				return;
			}
			else {
				range = std::max(range, static_cast<IType>(1e-3f));
			}
			// Get a big enough chunk size, bigger than range / n
			// (multiply by 2 is a safe factor)
			const IType chunk = 2 * range / n;
			// minimized range
			IType mrange = 0;
			// calculate minimized range: the max range for non big chunk
			{
				// first scan, grab all the big chunk
				// moving block index, exclude the two ends.
				size_t bid = 0;
				for (size_t i = 1; i < src.data.size() - 1; ++i) {
					// detect big chunk data point in the middle
					// always save these data points.
					//check if first arguement is big chunk
					if (CheckLarge(src.data[i], chunk)) {
						if (bid != i - 1) {
							// accumulate the range of the rest points
							mrange += src.data[i].RMaxPrev() - src.data[bid].RMinNext();
						}
						bid = i; ++nbig;
					}
				}
				//if the last big chunk isn't the last summary element, then add rest point between it and last element
				if (bid != src.data.size() - 2) {
					mrange += src.data[src.data.size() - 1].RMaxPrev() - src.data[bid].RMinNext();
				}
			}
			// assert: there cannot be more than n big data points
			if (nbig >= n) {
				// see what was the case
				/*LOG(INFO) << " check quantile stats, nbig=" << nbig << ", n=" << n;
				LOG(INFO) << " srcsize=" << src.size << ", maxsize=" << maxsize
				<< ", range=" << range << ", chunk=" << chunk;
				src.Print();
				CHECK(nbig < n) << "quantile: too many large chunk";*/
			}
			this->data.push_back(src.data[0]);
			//int size = 1;
			// The counter on the rest of points, to be selected equally from small chunks.
			n = n - nbig;
			// find the rest of point
			size_t bid = 0, k = 1, lastidx = 0;
			for (size_t end = 1; end < src.data.size(); ++end) {
				//if is large chunk or end element
				if (end == src.data.size() - 1 || CheckLarge(src.data[end], chunk)) {
					//if there is spacr between current big chunk and last big chunk
					if (bid != end - 1) {
						size_t i = bid;

						IType maxdx2 = src.data[end].RMaxPrev() * 2;
						//n here is the number of small chunk points
						for (; k <= n; ++k) {
							IType dx2 = 2 * ((k * mrange) / n + begin);
							//if (dx2 >= maxdx2) break;
							//debug
							//if (this->size == 171) {
							//	int check = 1;
							//}
							////debug
							//if (i == 226) {
							//	int check = 1;
							//}
							while (i < end &&
								dx2 >= src.data[i + 1].rmax + src.data[i + 1].rmin) ++i;
							if (i == end) break;
							if (lastidx == i) continue;
							////debug
							//if (size == 262) {
							//	int checkpoint = 0;
							//}
							if (dx2 < src.data[i].RMinNext() + src.data[i + 1].RMaxPrev()) {
								////debug
								//if (src.data[lastidx + 1].rmin == 532) {
								//	int check = 1;
								//}
								if (i != lastidx) {
									//mine
									Entry tempchunk = Entry(0, 0, 0, 0, 0, 0);
									if (lastidx + 1 != i) {
										tempchunk.value = src.data[(int)round((lastidx + 1 + i) / 2)].value;
									}
									else {
										tempchunk.value = src.data[lastidx + 1].value;
									}
									tempchunk.rmin = src.data[lastidx + 1].rmin;
									tempchunk.rmax = src.data[i].rmax;
									for (int l = lastidx + 1; l <= i; ++l) {
										tempchunk.scov += src.data[l].scov;
										tempchunk.sweight0 += src.data[l].sweight0;
										tempchunk.sweight1 += src.data[l].sweight1;
									}
									this->data.push_back(tempchunk); lastidx = i;
									//size++;
									//this->data[this->size++] = src.data[i]; lastidx = i;
								}
							}
							else {
								if (i + 1 != lastidx) {
									//mine
									Entry tempchunk = Entry(0, 0, 0, 0, 0, 0);
									if (lastidx + 1 != i + 1) {
										tempchunk.value = src.data[(int)round((lastidx + 1 + i + 1) / 2)].value;
									}
									else {
										tempchunk.value = src.data[lastidx + 1].value;
									}
									tempchunk.rmin = src.data[lastidx + 1].rmin;
									tempchunk.rmax = src.data[i + 1].rmax;
									for (int l = lastidx + 1; l <= i + 1; ++l) {
										tempchunk.scov += src.data[l].scov;
										tempchunk.sweight0 += src.data[l].sweight0;
										tempchunk.sweight1 += src.data[l].sweight1;
									}
									this->data.push_back(tempchunk); lastidx = i + 1; ++i;
									//size++;
									//this->data[this->size++] = src.data[i + 1]; lastidx = i + 1;
								}
							}
						}
					}
					if (lastidx != end) {
						if (lastidx + 1 < end) {
							Entry tempchunk = Entry(0, 0, 0, 0, 0, 0);
							if (lastidx + 2 != end) {
								tempchunk.value = src.data[(int)round((lastidx + end) / 2)].value;
							}
							else {
								tempchunk.value = src.data[lastidx + 1].value;
							}
							tempchunk.rmin = src.data[lastidx + 1].rmin;
							tempchunk.rmax = src.data[end - 1].rmax;
							for (int l = lastidx + 1; l <= end - 1; ++l) {
								tempchunk.scov += src.data[l].scov;
								tempchunk.sweight0 += src.data[l].sweight0;
								tempchunk.sweight1 += src.data[l].sweight1;
							}
							this->data.push_back(tempchunk);
							//size++;
							this->data.push_back(src.data[end]);
							//size++;
						}
						else {
							this->data.push_back(src.data[end]);
							//size++;
						}

						lastidx = end;
					}
					bid = end;
					// shift base by the gap
					begin += src.data[bid].RMinNext() - src.data[bid].RMaxPrev();
				}
			}
		}
	};


	/*!
	* \brief template for all quantile sketch algorithm
	*        that uses merge/prune scheme
	* \tparam FType type of data content
	* \tparam IType type of rank
	* \tparam TSummary actual summary data structure it uses
	*/
	template<typename FType, typename DType, typename IType,  class TSummary>
	class QuantileSketchTemplate {
	public:
		/*! \brief type of summary type */
		using Summary = TSummary;
		/*! \brief the entry type */
		using Entry = typename Summary::Entry;
		/*! \brief same as summary, but use STL to backup the space */
		struct SummaryContainer : public Summary {
			//std::vector<Entry> space;
			SummaryContainer(const SummaryContainer &src){
				this->data = src.data;
				//this->data = &(this->space)[0];
			}

			SummaryContainer(): Summary() {}
		
			/*!
			* \brief set the space to be merge of all Summary arrays
			* \param begin beginning position in the summary array
			* \param end ending position in the Summary array
			*/
			inline void SetMerge(const Summary *begin,
				const Summary *end) {
				//CHECK(begin < end) << "can not set combine to empty instance";
				size_t len = end - begin;
				if (len == 1) {
					//this->Reserve(begin[0].size);
					this->CopyFrom(begin[0]);
				}
				else if (len == 2) {
					//this->Reserve(begin[0].size + begin[1].size);
					this->SetMerge(begin[0], begin[1]);
				}
				else {
					// recursive merge
					SummaryContainer lhs, rhs;
					lhs.SetCombine(begin, begin + len / 2);
					rhs.SetCombine(begin + len / 2, end);
					//this->Reserve(lhs.size + rhs.size);
					this->SetCombine(lhs, rhs);
				}
			}
			/*!
			* \brief do elementwise combination of summary array
			*        this[i] = combine(this[i], src[i]) for each i
			* \param src the source summary
			* \param max_nbyte maximum number of byte allowed in here
			*/
			inline void Reduce(const Summary &src, size_t max_nbyte) {
				//this->Reserve((max_nbyte - sizeof(this->size)) / sizeof(Entry));
				SummaryContainer temp;
				//temp.Reserve(this->size + src.size);
				temp.SetCombine(*this, src);
				this->SetPrune(temp, data.size());
			}
			/*! \brief return the number of bytes this data structure cost in serialization */
			inline static size_t CalcMemCost(size_t nentry) {
				return sizeof(size_t) + sizeof(Entry) * nentry;
			}
			/*! \brief save the data structure into stream */
			template<typename TStream>
			inline void Save(TStream &fo) const {  // NOLINT(*)
				fo.Write(&(this->data.size()), sizeof(this->data.size()));
				if (this->data.size() != 0) {
					fo.Write(this->data, this->data.size() * sizeof(Entry));
				}
			}
			/*! \brief load data structure from input stream */
			template<typename TStream>
			inline void Load(TStream &fi) {  // NOLINT(*)
				CHECK_EQ(fi.Read(&this->data.size(), sizeof(this->data.size())), sizeof(this->data.size()));
				//this->Reserve(this->size);
				if (this->data.size() != 0) {
					CHECK_EQ(fi.Read(this->data, this->data.size() * sizeof(Entry)),
						this->data.size() * sizeof(Entry));
				}
			}
		};
		/*!
		* \brief initialize the quantile sketch, given the performance specification
		* \param maxn maximum number of data points can be feed into sketch
		* \param eps accuracy level of summary
		*/
		inline void Init(size_t maxn, float eps, double alpha, double beta) {
			LimitSizeLevel(maxn, eps, &nlevel, &limit_size);
			// lazy reserve the space, if there is only one value, no need to allocate space
			_alpha = alpha;
			_beta = beta;
			inqueue._alpha= alpha;
			inqueue._beta = beta;
			inqueue.queue.resize(0);
			inqueue.qtail = 0;
			temp.data.clear();
			//data.clear();
			level.clear();
		}

		inline static void LimitSizeLevel
		(size_t maxn, float eps, size_t* out_nlevel, size_t* out_limit_size) {
			size_t& nlevel = *out_nlevel;
			size_t& limit_size = *out_limit_size;
			nlevel = 1;
			while (true) {
				limit_size = static_cast<size_t>(ceil(nlevel / eps)) + 1;
				size_t n = (1ULL << nlevel);
				if (n * limit_size >= maxn) break;
				++nlevel;
			}
			// check invariant
			size_t n = (1ULL << nlevel);
			/* CHECK(n * limit_size >= maxn) << "invalid init parameter";
			CHECK(nlevel <= limit_size * eps) << "invalid init parameter";*/
		}

		/*!
		* \brief add an element to a sketch
		* \param x The element added to the sketch
		* \param w The weight of the element.
		*/
		inline void Push(IType label, DType x, IType w = 1) {
			if (w == static_cast<IType>(0)) return;
			//debug
			if (inqueue.qtail == 36) {
				int check = 1;
			}
			if (inqueue.qtail == limit_size * 2) {
				// jump from lazy one value to limit_size * 2
				//if (inqueue.queue.size() == 1) {
				//	inqueue.queue.resize(limit_size * 2);
				//}
				//else {
					//temp.Reserve(limit_size * 2);
				inqueue.MakeSummary(&temp);
				//penalize previous level
				std::vector<Summary>::iterator l;
				for (l = level.begin(); l != level.end(); ++l) {
					if (l->data.size() != 0) {
						for (std::vector<Entry>::iterator it = l->data.begin(); it != l->data.end(); ++it) {
							it->sweight0 = exp(log(it->sweight0) + (inqueue.qtail) * log(_alpha));
							it->sweight1 = exp(log(it->sweight1) + (inqueue.qtail) * log(_alpha));
						}
					}
				}
				// cleanup queue
				inqueue.qtail = 0;
				inqueue.queue.resize(0);
				this->PushTemp();
				//}
			}
			inqueue.Push(label, x, w);
		}

		inline void PushSparse(IType label, DType x, IType c, DType w, int follow) {
			if (c == static_cast<IType>(0)) return;
			if (inqueue.qtail >= limit_size * 2 & follow == 0) {
				// jump from lazy one value to limit_size * 2
				//if (inqueue.queue.size() == 1) {
				//	inqueue.queue.resize(limit_size * 2);
				//}
				//else {
					//temp.Reserve(limit_size * 2);
				inqueue.MakeSummary(&temp);
				//penalize previous level
				std::vector<Summary>::iterator l;
				for (l = level.begin(); l != level.end(); ++l) {
					if (l->data.size() != 0) {
						for (std::vector<Entry>::iterator it = l->data.begin(); it != l->data.end(); ++it) {
							it->sweight0 = exp(log(it->sweight0) + (inqueue.qtail) * log(_alpha));
							it->sweight1 = exp(log(it->sweight1) + (inqueue.qtail) * log(_alpha));
						}
					}
				}
				// cleanup queue
				inqueue.qtail = 0;
				inqueue.queue.resize(0);
				this->PushTemp();
				//}
			}
			inqueue.PushSparse(label, x, c, w);
		}


		/*! \brief push up temp */
		inline void PushTemp() {
			//temp.Reserve(limit_size * 2);
			for (size_t l = 1; true; ++l) {
				this->InitLevel(l + 1);
				// check if level l is empty
				if (level[l].data.size() == 0) {
					level[l].SetPrune(temp, limit_size);
					temp.data.clear();
					break;
				}
				else {
					// level 0 is actually temp space
					level[0].SetPrune(temp, limit_size);
					temp.data.clear();
					//debug:
					//if (level[0].size == 385) {
					//	int a = 1;
					//}
					temp.SetCombine(level[0], level[l]);
					level[0].data.clear();
					if (temp.data.size() > limit_size) {
						// try next level
						level[l].data.clear();
					}
					else {
						// if merged record is still smaller, no need to send to next level
						level[l].CopyFrom(temp); 
						temp.data.clear();
						break;
					}
				}
			}
		}

		/*! \brief get the summary after finalize */
		inline void GetSummary(SummaryContainer *out, float eps) {
			//if (level.size() != 0) {
			//	out->Reserve(limit_size * 2);
			//}
			//else {
			//	out->Reserve(inqueue.queue.size());
			//}
			inqueue.MakeSummary(out);
			//penalize previous level
			std::vector<Summary>::iterator l;
			for (l = level.begin(); l != level.end(); ++l) {
				if (l->data.size() != 0) {
					for (std::vector<Entry>::iterator it = l->data.begin(); it != l->data.end(); ++it) {
						it->sweight0 = exp(log(it->sweight0) + (inqueue.qtail) * log(_alpha));
						it->sweight1 = exp(log(it->sweight1) + (inqueue.qtail) * log(_alpha));
					}
				}
			}
			if (level.size() != 0) {
				level[0].SetPrune(*out, limit_size);
				for (size_t l = 1; l < level.size(); ++l) {
					if (level[l].data.size() == 0) continue;
					if (level[0].data.size() == 0) {
						//level[0].CopyFrom(level[l]);
						cout << "level[0].CopyFrom(level[l])" << endl;
					}
					else {
						temp.SetCombine(level[0], level[l]);
						level[0].CopyFrom(temp);
						temp.data.clear();
					}
				}
				out->data.clear();
				out->SetPrune(level[0], static_cast<size_t>(ceil(2 / eps)));
				level[0].data.clear();
			}
			else {
				//if (out->data.size() > limit_size) {
					//temp.Reserve(limit_size);
				temp.SetPrune(*out, limit_size);
				out->data.clear();
				out->SetPrune(temp, static_cast<size_t>(ceil(2 / eps)));
				temp.data.clear();
				//}
			}
		}
		// used for debug, check if the sketch is valid
		inline void CheckValid(FType eps) const {
			for (size_t l = 1; l < level.size(); ++l) {
				level[l].CheckValid(eps);
			}
		}
		// initialize level space to at least nlevel
		inline void InitLevel(size_t nlevel) {
			if (level.size() >= nlevel) return;
			//data.resize(limit_size * nlevel);
			level.resize(nlevel);
			//for (size_t l = 0; l < level.size(); ++l) {
			//	level[l].data = &data[0] + l * limit_size;
			//}
		}
		// input data queue
		typename Summary::Queue inqueue;
		// number of levels
		size_t nlevel;
		// size of summary in each level
		size_t limit_size;
		// influence rate
		double _alpha, _beta;
		// the level of each summaries
		std::vector<Summary> level;
		// content of the summary
		//std::vector<Entry> data;
		// temporal summary, used for temp-merge
		SummaryContainer temp;
	};


	/*!
	* \brief Quantile sketch use WXQSummary
	* \tparam FType type of data content
	* \tparam IType type of rank
	*/
	template<typename FType, typename DType, typename IType = unsigned>
	class WXQuantileSketch :
		public QuantileSketchTemplate<FType, DType, IType,  WXQSummary<FType, DType, IType> > {
	};
	
}  
#endif  

