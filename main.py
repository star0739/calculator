import math
import streamlit as st


st.set_page_config(page_title="계산기 웹앱", page_icon="🧮", layout="centered")
st.title("🧮 계산기 웹앱 (키패드 입력)")
st.caption("키패드로 숫자를 입력하고, 사칙연산 · 모듈러 · 지수 · 로그를 계산합니다.")


# -----------------------------
# 상태 초기화
# -----------------------------
def init_state():
    defaults = {
        "a_str": "0",
        "b_str": "0",
        "base_str": "10",
        "active_field": "a",   # "a" | "b" | "base"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# -----------------------------
# 유틸
# -----------------------------
def safe_float(x: str) -> float:
    x = x.strip().replace(",", "")
    return float(x)


def compute(op: str, a: float, b: float | None, log_base: float | None) -> float:
    if op == "덧셈 (+)":
        return a + b
    if op == "뺄셈 (-)":
        return a - b
    if op == "곱셈 (×)":
        return a * b
    if op == "나눗셈 (÷)":
        if b == 0:
            raise ZeroDivisionError("0으로 나눌 수 없습니다.")
        return a / b
    if op == "모듈러 (%)":
        if b == 0:
            raise ZeroDivisionError("0으로 나눈 나머지는 정의되지 않습니다.")
        return a % b
    if op == "지수 (a^b)":
        return a ** b
    if op == "로그 (log_base(a))":
        if a <= 0:
            raise ValueError("로그의 진수(a)는 0보다 커야 합니다.")
        if log_base is None:
            raise ValueError("로그의 밑(base)을 입력해야 합니다.")
        if log_base <= 0 or log_base == 1:
            raise ValueError("로그의 밑(base)은 0보다 커야 하고 1이 아니어야 합니다.")
        return math.log(a, log_base)

    raise ValueError("지원하지 않는 연산입니다.")


def get_field_value(field: str) -> str:
    if field == "a":
        return st.session_state["a_str"]
    if field == "b":
        return st.session_state["b_str"]
    if field == "base":
        return st.session_state["base_str"]
    raise ValueError("알 수 없는 필드입니다.")


def set_field_value(field: str, value: str) -> None:
    if field == "a":
        st.session_state["a_str"] = value
        return
    if field == "b":
        st.session_state["b_str"] = value
        return
    if field == "base":
        st.session_state["base_str"] = value
        return
    raise ValueError("알 수 없는 필드입니다.")


def normalize_number_str(s: str) -> str:
    """입력 문자열을 계산기스럽게 정리(선행 0, 빈값 등)."""
    s = s.strip()
    if s == "" or s == "-":
        return s
    # "000" -> "0", "000.1" -> "0.1"
    if s.startswith("-"):
        sign = "-"
        body = s[1:]
    else:
        sign = ""
        body = s

    if body == "":
        return s

    if body.startswith("0") and len(body) > 1 and not body.startswith("0."):
        # 0으로 시작하고 0.이 아니면 앞의 0 제거
        body = body.lstrip("0")
        if body == "" or body.startswith("."):
            body = "0" + body

    return sign + body


def append_char(ch: str) -> None:
    field = st.session_state["active_field"]
    cur = get_field_value(field)

    # 초기값 "0"일 때 숫자 입력이면 치환(0 -> 7)
    if cur == "0" and ch.isdigit():
        cur = ch
    else:
        # '.'는 1회만 허용
        if ch == "." and "." in cur:
            return
        cur = cur + ch

    set_field_value(field, normalize_number_str(cur))


def toggle_sign() -> None:
    field = st.session_state["active_field"]
    cur = get_field_value(field).strip()
    if cur.startswith("-"):
        cur = cur[1:]
        if cur == "":
            cur = "0"
    else:
        if cur == "" or cur == "0":
            cur = "-0"
        else:
            cur = "-" + cur
    set_field_value(field, normalize_number_str(cur))


def backspace() -> None:
    field = st.session_state["active_field"]
    cur = get_field_value(field)
    if cur == "" or cur == "0":
        return
    cur = cur[:-1]
    if cur == "" or cur == "-":
        cur = "0"
    set_field_value(field, normalize_number_str(cur))


def clear_active() -> None:
    field = st.session_state["active_field"]
    set_field_value(field, "0")


def clear_all() -> None:
    st.session_state["a_str"] = "0"
    st.session_state["b_str"] = "0"
    st.session_state["base_str"] = "10"


# -----------------------------
# 연산 선택
# -----------------------------
operation = st.selectbox(
    "연산을 선택하세요",
    [
        "덧셈 (+)",
        "뺄셈 (-)",
        "곱셈 (×)",
        "나눗셈 (÷)",
        "모듈러 (%)",
        "지수 (a^b)",
        "로그 (log_base(a))",
    ],
)

st.divider()

# -----------------------------
# 입력 대상 선택 + 표시
# -----------------------------
needs_b = operation in ["덧셈 (+)", "뺄셈 (-)", "곱셈 (×)", "나눗셈 (÷)", "모듈러 (%)", "지수 (a^b)"]
needs_base = operation == "로그 (log_base(a))"

field_options = ["a"]
if needs_b:
    field_options.append("b")
if needs_base:
    field_options.append("base")

labels = {"a": "a(첫 번째 값)", "b": "b(두 번째 값)", "base": "base(로그 밑)"}

st.radio(
    "키패드로 입력할 값을 선택하세요",
    options=field_options,
    format_func=lambda x: labels[x],
    horizontal=True,
    key="active_field",
)

# 표시용 입력칸(직접 타이핑도 가능)
colA, colB, colC = st.columns(3 if (needs_b or needs_base) else 1)
with colA:
    st.text_input("a", key="a_str")
if needs_b:
    with colB:
        st.text_input("b", key="b_str")
if needs_base:
    with colC:
        st.text_input("base", key="base_str")

st.caption("입력 선택(라디오) 후 아래 키패드 버튼으로 숫자를 넣을 수 있습니다.")

st.divider()

# -----------------------------
# 키패드(실물 계산기 배열 느낌)
# -----------------------------
# 7 8 9 ⌫
# 4 5 6 ±
# 1 2 3 C
# 0 . 00 AC

r1 =
