# encoding:utf-8
from __future__ import annotations
from fractions import Fraction


def ERROR(args, typeList):
    for arg in args:
        is_valid = False
        for t in typeList:
            if isinstance(arg, t):
                is_valid = True
                break
        if not is_valid:
            raise TypeError("The arg must be one of the following types: " + str(typeList) + ".")


class MathFraction(Fraction):
    math_fraction_type = None
    current = Fraction(0)

    def __new__(cls, n, d, isOuter=True):
        # 类型检查
        ERROR([n, d], [int, float])
        if d == 0:
            raise ZeroDivisionError("Denominator cannot be zero")

        # 处理浮点数并化简
        if isinstance(n, float):
            n = Fraction(str(n))
        if isinstance(d, float):
            d = Fraction(str(d))
        frac = Fraction(n, d)

        # 关键修复：使用父类的__new__正确初始化实例
        instance = super().__new__(cls, frac.numerator, frac.denominator)
        return instance

    def __init__(self, n, d, isOuter=True):
        # 不需要手动设置_denominator和_numerator，父类已处理
        self.n = self._numerator  # 复用父类的属性
        self.d = self._denominator

    class ProperFraction(MathFraction):
        def __new__(cls, n, d, isOuter=True):
            # 1. 复用父类逻辑：类型检查、处理浮点数、化简分数
            # （调用MathFraction的__new__处理基础逻辑，但不直接返回，先做真分数校验）
            # 注意：这里用super()调用父类MathFraction的__new__
            temp_instance = super().__new__(cls, n, d, isOuter)

            # 2. 真分数核心校验：分子绝对值必须 < 分母绝对值
            # 从临时实例中获取化简后的分子分母（父类已处理）
            numerator = temp_instance._numerator
            denominator = temp_instance._denominator

            if abs(numerator) >= abs(denominator) and isOuter:
                # isOuter=True表示外部主动创建，严格校验；内部创建（如运算结果）可放宽
                raise ValueError("真分数必须满足：|分子| < |分母|")

            # 3. 返回校验通过的实例（此时已确保是真分数）
            return temp_instance

        def __init__(self, n, d, isOuter=True):
            # 复用父类初始化逻辑，无需重复编写
            super().__init__(n, d, isOuter)

    class ImproperFraction(MathFraction):
        def __new__(cls, n, d, isOuter=True):
            # 1. 复用父类逻辑：类型检查、处理浮点数、化简分数
            # （调用MathFraction的__new__处理基础逻辑，但不直接返回，先做假分数校验）
            # 注意：这里用super()调用父类MathFraction的__new__
            temp_instance = super().__new__(cls, n, d, isOuter)

            # 2. 假分数核心校验：分子绝对值必须 < 分母绝对值
            # 从临时实例中获取化简后的分子分母（父类已处理）
            numerator = temp_instance._numerator
            denominator = temp_instance._denominator

            if abs(numerator) < abs(denominator) and isOuter:
                # isOuter=True表示外部主动创建，严格校验；内部创建（如运算结果）可放宽
                raise ValueError("假分数必须满足：|分子| > |分母|")

            # 3. 返回校验通过的实例（此时已确保是假分数）
            return temp_instance

        def __init__(self, n, d, isOuter=True):
            # 复用父类初始化逻辑，无需重复编写
            super().__init__(n, d, isOuter)

    def fraction_class(self):
        if abs(MathFraction.current) < 1:
            MathFraction.current = MathFraction.ProperFracion(MathFraction.current.numerator,
                                                              MathFraction.current.denominator)
        else:
            MathFraction.current = MathFraction.ImproperFraction(MathFraction.current.numerator,
                                                                 MathFraction.current.denominator)


# 测试代码
if __name__ == "__main__":
    # 测试实例化和打印
    f = MathFraction(2, 4)  # 会被化简为1/2
    print(f)  # 应输出 1/2
