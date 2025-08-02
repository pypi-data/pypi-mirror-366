import pyphg as phg
import math

Cos, M_PI = math.cos, math.pi

# 定义边界函数和右端项
a = 1.0
def func_u(input):
    x, y, z = input
    value = Cos(2. * M_PI * x) * Cos(2. * M_PI * y) * Cos(2. * M_PI * z)
    return [value]

def func_f(input):
    value, = func_u(input)
    value = 12. * M_PI * M_PI * value + a * value
    return [value]

# 加载网格并加密一次
mesh = phg.Grid("../test/cube4.dat")
mesh.refineAllElements(4)

# 定义有限元函数，并设置初值
order = 1
u_h = phg.Dof(mesh, "P", order, name="u_h")
u_h.setDataByValue(0)
f_h = phg.Dof(mesh, "P", order, udf=func_f)

# 定义求解器
solver = phg.Solver("pcg", u_h)
print(f"DOF {u_h.getSize()}, {mesh.getNumElements()} elements")
# 对网格中的单元循环
for e in mesh.getElementIterator():
    # 计算单刚和单元荷载
    stiffmat = e.quadGradBasDotGradBas(u_h, u_h)
    massmat = e.quadBasDotBas(u_h, u_h)
    emat = stiffmat + a * massmat
    eload = e.quadDofTimesBas(f_h, u_h)
    # 获取单元自由度的全局编号
    gid = e.getGlobalIndex(solver)
    # 获取这个单元自由度是否为第一类边界，并处理第一类边界
    is_boundary, boundary_val = e.getDirichletBC(u_h, func_u)
    phg.utils.processBoundary(is_boundary, boundary_val, emat, eload)
    # 将单刚和单元荷载加到总刚
    solver.addMatrixEntries(gid, gid, emat)
    solver.addRHSEntries(gid, eload)

# 求解
solver.setSymmetry(solver.SPD)
solver.solve(u_h)

print(solver)
# 导出有限元解到后处理软件
mesh.exportVTK("simplest_py.vtk", u_h)

