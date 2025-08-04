import sympy 
import json
def quadratic_equation(a:float,b:float,c:float)->str:
    try:
        x=sympy.symbols('x')
        equation=sympy.Eq(a*x**2+b*x+c,0)
        solutions=sympy.solve(equation,x)
        solutions_str=[str(sol) for sol in solutions]
        return json.dumps({"roots":solutions_str})
    except Exception as e:
        return json.dumps({"error": f"Failed to solve quadratic equation: {e}"})