# 界面 QtApplication

- 编排

最左：QVBoxLayout 用一个QFrame将其包含，因为Frame是一个Widget（组件）可以做到随时隐藏，随时显示
而对于Layout而言，只能通过遍历其中的组件，将组件一个一个的隐藏才能完成对layout及其元素的隐藏。之所以要隐藏，是因为添加系列光线与添加单条光线不同同时存在，为了不发生错误，隐藏起来直接禁止用户同时输入两种数据反而更加安全。
Start point表示起点，V表示光线的方向向量，由此可以确定一条入射光线；将当前的数据加入计算的入射光线中，按add按钮。
delete前面的选项框表示需要删除的行数，对应的，删除了对应的入射光线，则会在下次计算时去除。
clear 表示清空所有数据。

对于当前的数据可以保存为一个csv文件，方便下次使用时，不用重新一条一条的输入。
csv文件的格式为：第一行为表头
start_point vector   
（数据点1）， （向量1）

起始点与向量在界面中使用表格展示，对这些数据进行操作时，要时刻保持表格的更新，这样才能保证后台数据与前端显示一致。

中间：
下拉框决定是否使用连续光线的生成器，选择是时将隐藏左侧数据输入的边栏。
往下是参数输入部分，再往下是作图区域，即matplotlib的Canvas实例，实现matplotlib嵌入到PyQt的功能，底部的工具栏也是matplotlib的图形工具栏，这样对于其的使用会有较少的问题出现。


右侧：
数据输出部分。
分别显示第几次作用的出射角度。


# 3D funcs

## Functions

- drawer
- multi_line_drawer

### drawer

Single light drawer.
parameter:
`@sphere: One of the intersectionElements class`  Define the sphere with certain radius and center
`@incident_light: One of the intersectionElements class`  see Elements about light.
`@refraction_index: Definition of the refraction index inside the sphere`  
`@start_point: The coordinates of the starting point` Tuple or list contains three float numbers.
`@intersection_time: Times of the intersection` How many times the light intersect the sphere.

Return:
`dict`  
`points: the intersection points` `list`  first intersection: points[0] second intersection point: points[1] etc.
`lines: the lines to draw in the figre` `list` 
