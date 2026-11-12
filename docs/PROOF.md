# 四边形薄板质心公式与辅助圆构造的证明

## 1. 定理

设 $ABCD$ 是按边界顺序排列的严格凸四边形，$E=AC\cap BD$，$M,N$ 分别为 $AC,BD$ 的中点。均匀薄板的质心唯一，且满足

$$\boxed{G=\frac{A+B+C+D-E}{3}=\frac{2M+2N-E}{3}.}$$

若 $V$ 为 $MN$ 的中点，则

$$\boxed{G=\frac{4V-E}{3},\qquad \overrightarrow{VG}=\frac13\overrightarrow{EV}.}$$

[完整作法](ANSWER.md) 在全部合法输入上有限完成，并输出这个点。

以下向量等式可在任意固定原点下理解。各仿射组合的系数和为一。

## 2. 三角形的面积质心与拼合

对非退化三角形 $PQR$，以

$$X=P+u(Q-P)+v(R-P),\qquad u,v\ge0,\quad u+v\le1$$

参数化内部。参数三角形上的积分满足

$$\iint1\,\mathrm du\,\mathrm dv=\frac12,\qquad
\iint u\,\mathrm du\,\mathrm dv=\iint v\,\mathrm du\,\mathrm dv=\frac16.$$

仿射映射的面积雅可比为常数，所以均匀三角形的质心为

$$G_{PQR}=\frac{P+Q+R}{3}.$$

若一个区域由内部互不相交、面积为 $S_1,S_2$ 的两个三角形拼成，则面积积分可加，整体质心为

$$G=\frac{S_1G_1+S_2G_2}{S_1+S_2}.$$

边界的面积为零。四边形面积为正，故这个积分表达式定义一个唯一的点。两个三角形质心均在四边形内部，正权重平均也在内部。

## 3. 从面积加权推出四边形公式

沿 $AC$ 分割为 $ABC$ 与 $ACD$。记

$$s=BE>0,\qquad t=ED>0.$$

由于 $B,E,D$ 共线，且 $E$ 位于 $BD$ 内部，两三角形到共同底边 $AC$ 的高之比为 $s:t$，所以

$$[ABC]:[ACD]=s:t.$$

记两三角形质心为

$$U=\frac{A+B+C}{3}=\frac{2M+B}{3},\qquad
W=\frac{A+C+D}{3}=\frac{2M+D}{3}.$$

面积加权给出

$$G=\frac{sU+tW}{s+t}
=\frac13\left(2M+\frac{sB+tD}{s+t}\right).$$

令 $v$ 为从 $E$ 指向 $B$ 的单位向量，则 $B=E+sv$、$D=E-tv$。于是

$$\frac{sB+tD}{s+t}=E+(s-t)v=B+D-E=2N-E.$$

代回即得

$$G=\frac{2M+2N-E}{3}=\frac{A+B+C+D-E}{3}.$$

这个推导只使用严格凸四边形的对角线内部相交性质，覆盖对称和中点重合的输入。顺时针编号时面积仍取正值，相同推导成立。

## 4. 辅助圆取得两个反射点

先考虑 $M\ne E$ 且 $N\ne E$。

两条对角线相交，所以其垂直平分线唯一交于 $F$。因为 $FM\perp AC$、$FN\perp BD$，$M,N$ 分别为 $F$ 在两条对角线上的垂足。

若 $F=E$，则 $E$ 同时位于两条对角线的垂直平分线上，推出 $M=N=E$，与本分支条件矛盾。因此圆 $\omega(F,FE)$ 有正半径。

将 $E$ 关于 $M$ 反射得到 $I=2M-E$。点 $F$ 位于 $EI$ 的垂直平分线上，所以 $FI=FE$，即 $I\in\omega$。同时 $I\in AC$，并且 $M\ne E$ 保证 $I\ne E$，故 $I$ 正是直线 $AC$ 上的另一个圆交点。

同理，直线 $BD$ 上的另一个交点为

$$J=2N-E.$$

由于 $E$ 在每条对角线段内部，反射点 $I=A+C-E$ 位于 $AC$ 严格内部，$J=B+D-E$ 位于 $BD$ 严格内部。

## 5. 两条连接线唯一交于薄板质心

非零向量 $EI,EJ$ 分别沿两条不同对角线，因此三角形 $EIJ$ 非退化。

$M$ 是 $EI$ 的中点，$N$ 是 $EJ$ 的中点，所以 $MJ,NI$ 是它的两条中线。两中线唯一交于三角形质心

$$K=\frac{E+I+J}{3}
=\frac{E+(2M-E)+(2N-E)}3
=\frac{2M+2N-E}{3}.$$

由第 3 节，$K=G$，主构造成立。并有

$$G=M+\frac13(J-M)=N+\frac13(I-N).$$

这也明确了交点在两条中线上的次序与分点比例。

## 6. 特殊分支

### 仅 $M=E$

公式化为

$$G=\frac{E+2N}{3}=E+\frac23(N-E).$$

因 $N\ne E$，第 5 节三等分作法适用。此时 $F$ 在过 $E$ 的 $AC$ 垂线上，圆在 $E$ 与 $AC$ 相切。若将 $I$ 取为 $E$，则 $NI,MJ$ 都是 $BD$。

### 仅 $N=E$

对称地，

$$G=E+\frac23(M-E).$$

圆在 $E$ 与 $BD$ 相切，原两条连接线都为 $AC$。同样用三等分分支完成。

### $M=N=E$

两条对角线互相平分，四边形为平行四边形。公式给出 $G=E$。此时 $F=E$，直接输出已有点即可。

四种条件互斥且覆盖全部输入。原题辅助圆法在两个中点均与 $E$ 不同的分支中成立。

## 7. 与四顶点平均点的关系

因 $V=(M+N)/2$，有 $4V=2M+2N$，故

$$G-V=\frac{V-E}{3}.$$

在非平行四边形情形，$V\ne E$。否则 $M-E=-(N-E)$，而这两个向量分别沿不同的对角线，只能同时为零，推出平行四边形。

所以非平行四边形中 $E,V,G$ 依次共线，且

$$EV:VG=3:1.$$

平行四边形中三点重合。一般情况下 $V$ 与 $G$ 的位移精确为 $\tfrac13\overrightarrow{EV}$。

## 8. 有限性与独立核验

两条对角线及其垂直平分线分别唯一相交。主分支中的两个圆交点由第 4 节保证，两条中线的唯一交点由第 5 节保证。特殊分支中的辅助点来自另一条对角线，保证三等分作法中的三角形非退化。所有尺规宏均有固定有限展开。

[数据生成与核验脚本](../animations/centroid/export_geometry.py) 在精确实代数数域中求交、选择交点和重放特殊分支。核验器独立使用多边形边界的一阶矩公式

$$c_i=x_i y_{i+1}-x_{i+1}y_i,\qquad
G_x=\frac{\sum_i(x_i+x_{i+1})c_i}{3\sum_i c_i},\qquad
G_y=\frac{\sum_i(y_i+y_{i+1})c_i}{3\sum_i c_i}.$$

该式由面积积分的边界表达式得到，顺时针编号时分子分母同时变号。脚本将实际作图交点与此式及第 1 节公式精确比较，并检查变换和特殊案例。[运行方式与实际结果](../animations/centroid/README.md)

## 9. 来源与整理范围

原题给出辅助圆、对角线中点及两条连接线的作法。原问答中的面积加权与反射点关系提供了证明线索。本项目采用统一记号，将最后的相交关系解释为三角形的两条中线，补齐相切、直线重合与零半径分支，并提供对应动画和精确核验。[题集原题及原回答](https://github.com/lenovobenben/ai-math-notes/blob/main/chatgpt/经典数学题100例-5/001_尺规作图证明__69450073-f448-8320-9231-5196c6c41222/001_尺规作图证明__69450073-f448-8320-9231-5196c6c41222.md)

项目依据系列路线图第九题。路线图另列 John Boris Miller 的 *Centroid of a Quadrilateral* 为相关文献。[研究路线图](https://github.com/lenovobenben/euclid-conic-classification/blob/main/docs/Euclid十题研究路线图.md) · [Miller 文献入口](https://www.austms.org.au/wp-content/uploads/Gazette/2010/May10/TechPaperMiller.pdf)
