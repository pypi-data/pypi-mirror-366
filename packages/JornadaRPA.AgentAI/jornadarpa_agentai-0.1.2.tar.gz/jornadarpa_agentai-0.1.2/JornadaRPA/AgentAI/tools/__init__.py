from .calculator import run_tool as calculator
from .date_tool import run_tool as date
from .reverse_tool import run_tool as reverse
from .length_tool import run_tool as length
from .uppercase_tool import run_tool as uppercase
from .lowercase_tool import run_tool as lowercase
from .contains_tool import run_tool as contains
from .countwords_tool import run_tool as countwords
from .extractnum_tool import run_tool as extractnum

TOOLS = {
    "calculator": calculator,
    "date": date,
    "reverse": reverse,
    "length": length,
    "uppercase": uppercase,
    "lowercase": lowercase,
    "contains": contains,
    "countwords": countwords,
    "extractnum": extractnum,
}