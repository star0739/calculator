import math
from typing import Optional

import streamlit as st


st.set_page_config(page_title="계산기 웹앱", page_icon="🧮", layout="centered")
st.title("🧮 계산기 웹앱 (키패드 입력)")
st.caption("키패드로 숫자를 입력하고, 사칙연산 · 모듈러 · 지수 · 로그를 계산합니다.")


# -----------------------------
# 상태 초기화
# -----------------------------
def init_state() -> None:
    defaults = {
        "a_str": "0",
        "b_str": "0",
        "base_str": "10",
        "active_field": "a",  # "a" | "b" | "base"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# -----------------------------
# 유틸
# -----------------------------
def safe_float(x: str) -> float:
    """
    문자열을 float로 변환합니다.
    쉼표(,) 입력을 허용하기 위해 제거 후 변환합니다.
    """
    x = x.strip().replace(",", "")
    return float(x)


def compute(op: str, a: float, b: Optional[float], log_base: Optional[float]) -> float:
    """
    op에 따라 연산을 수행하고 결과를 반환합니다.
    b 또는 log_base는 op에 따라 None일 수 있습니다.
    """
    if op == "덧셈 (+)":
        return a + float(b)
    if op == "뺄셈 (-)":
        return a - float(b)
    if op == "곱셈 (×)":
        return a * float(b)
    if op == "나눗셈 (÷)":
        if float(b) == 0:
            raise ZeroDivisionError("0으로 나눌 수 없습니다.")
        return a / float(b)
    if op == "모듈러 (%)":
        if float(b) == 0:
            raise ZeroDivisionError("0으로 나눈 나머지는 정의되지 않습니다.")
        return a % float(b)
    if op == "지수 (a^b)":
        return a ** float(b)
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
    """
    계산기 입력 문자열을 정리합니다.
    - 빈값, '-' 단독 허용
    - 선행 0 처리 (0.은 유지)
    """
    s = s.strip()
    if s == "" or s == "-":
        return s

    # 부호 분리
    sign = ""
    body = s
    if s.startswith("-"):
        sign = "-"
        body = s[1:]

    if body == "":
        return s

    # 선행 0 제거(단, "0."은 유지)
    if body.startswith("0") and len(body) > 1 and not body.startswith("0."):
        body = body.lstrip("0")
        if body == "" or body.startswith("."):
            body = "0" + body

    return sign + body


def append_char(ch: str) -> None:
    field = st.session_state["active_field"]
    cur = get_field_value(field)

    # 초기값 "0"에서 숫자를 누르면 치환
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
    # base는 기본값 10으로 두는 편이 실사용에 편리하므로 base만 예외 처리
    if field == "base":
        set_field_value(field, "10")
    else:
        set_field_value(field, "0")


def clear_all() -> None:
    st.session_state["a_str"] = "0"
    st.session_state["b_str"] = "0"
    st.session_state["base_str"] = "10"
    st.session_state["active_field"] = "a"


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

needs_b = operation in [
    "덧셈 (+)",
    "뺄셈 (-)",
    "곱셈 (×)",
    "나눗셈 (÷)",
    "모듈러 (%)",
    "지수 (a^b)",
]
needs_base = operation == "로그 (log_base(a))"

st.divider()

# -----------------------------
# 입력 대상 선택 + 표시(타이핑도 가능)
# -----------------------------
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

# 표시용 입력칸
cols = st.columns(3)
with cols[0]:
    st.text_input("a", key="a_str")

with cols[1]:
    if needs_b:
        st.text_input("b", key="b_str")
    else:
        st.text_input("b (해당 연산에서 미사용)", value=st.session_state["b_str"], disabled=True)

with cols[2]:
    if needs_base:
        st.text_input("base", key="base_str")
    else:
        st.text_input("base (해당 연산에서 미사용)", value=st.session_state["base_str"], disabled=True)

st.caption("라디오에서 입력 대상을 선택한 뒤, 아래 키패드로 숫자를 입력하세요.")
st.divider()

# -----------------------------
# 키패드(실물 계산기 배열 느낌)
# -----------------------------
# 7 8 9 ⌫
# 4 5 6 ±
# 1 2 3 C
# 0 . 00 AC

r1 = st.columns(4)
if r1[0].button("7", use_container_width=True):
    append_char("7")
if r1[1].button("8", use_container_width=True):
    append_char("8")
if r1[2].button("9", use_container_width=True):
    append_char("9")
if r1[3].button("⌫", use_container_width=True):
    backspace()

r2 = st.columns(4)
if r2[0].button("4", use_container_width=True):
    append_char("4")
if r2[1].button("5", use_container_width=True):
    append_char("5")
if r2[2].button("6", use_container_width=True):
    append_char("6")
if r2[3].button("±", use_container_width=True):
    toggle_sign()

r3 = st.columns(4)
if r3[0].button("1", use_container_width=True):
    append_char("1")
if r3[1].button("2", use_container_width=True):
    append_char("2")
if r3[2].button("3", use_container_width=True):
    append_char("3")
if r3[3].button("C", use_container_width=True):
    clear_active()

r4 = st.columns(4)
if r4[0].button("0", use_container_width=True):
    append_char("0")
if r4[1].button(".", use_container_width=True):
    append_char(".")
if r4[2].button("00", use_container_width=True):
    append_char("00")
if r4[3].button("AC", use_container_width=True):
    clear_all()

st.divider()

# -----------------------------
# 계산 실행
# -----------------------------
calc_col1, calc_col2 = st.columns([1, 1])
with calc_col1:
    do_calc = st.button("계산", type="primary", use_container_width=True)
with calc_col2:
    st.button("전체 초기화", on_click=clear_all, use_container_width=True)

if do_calc:
    try:
        a = safe_float(st.session_state["a_str"])

        b = None
        if needs_b:
            b = safe_float(st.session_state["b_str"])

        log_base = None
        if needs_base:
            log_base = safe_float(st.session_state["base_str"])

        # 필요 값 누락 방지
        if needs_b and b is None:
            raise ValueError("b 값이 필요합니다.")
        if needs_base and log_base is None:
            raise ValueError("base 값이 필요합니다.")

        result = compute(operation, a, b, log_base)

        st.success("계산이 완료되었습니다.")
        st.metric(label="결과", value=str(result))

        with st.expander("자세히 보기"):
            st.write(
                {
                    "operation": operation,
                    "a": a,
                    "b": b,
                    "base": log_base,
                    "result": result,
                }
            )

    except ValueError as e:
        st.error(f"입력 오류: {e}")
    except ZeroDivisionError as e:
        st.error(f"연산 오류: {e}")
    except Exception as e:
        st.error(f"알 수 없는 오류: {e}")
