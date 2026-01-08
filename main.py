import math
import streamlit as st


st.set_page_config(page_title="계산기 웹앱", page_icon="🧮", layout="centered")

st.title("🧮 계산기 웹앱 (Streamlit)")
st.caption("사칙연산 · 모듈러 · 지수 · 로그 기능을 제공합니다.")


def safe_float(x: str) -> float:
    """
    문자열을 float로 변환합니다.
    쉼표(,) 입력을 허용하기 위해 제거 후 변환합니다.
    """
    x = x.strip().replace(",", "")
    return float(x)


def compute(op: str, a: float, b: float | None, log_base: float | None) -> float:
    """
    op에 따라 연산을 수행하고 결과를 반환합니다.
    b 또는 log_base는 op에 따라 None일 수 있습니다.
    """
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
        # 파이썬의 거듭제곱은 a**b
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


# 연산 선택
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

# 입력 UI: 연산 종류에 따라 필요한 입력을 다르게 받기
# a는 항상 필요
a_str = st.text_input("첫 번째 값 (a)", value="0")

b_str = None
base_str = None

if operation in ["덧셈 (+)", "뺄셈 (-)", "곱셈 (×)", "나눗셈 (÷)", "모듈러 (%)", "지수 (a^b)"]:
    b_str = st.text_input("두 번째 값 (b)", value="0")

if operation == "로그 (log_base(a))":
    base_str = st.text_input("로그의 밑 (base)", value="10")

# 계산 버튼
col1, col2 = st.columns([1, 1])
with col1:
    do_calc = st.button("계산", type="primary")
with col2:
    st.button("초기화", on_click=lambda: st.session_state.clear())

if do_calc:
    try:
        a = safe_float(a_str)

        b = None
        if b_str is not None:
            b = safe_float(b_str)

        log_base = None
        if base_str is not None:
            log_base = safe_float(base_str)

        result = compute(operation, a, b, log_base)

        st.success("계산이 완료되었습니다.")
        st.metric(label="결과", value=f"{result}")

        # 참고 출력(선택)
        with st.expander("자세히 보기"):
            st.write({"operation": operation, "a": a, "b": b, "base": log_base, "result": result})

    except ValueError as e:
        st.error(f"입력 오류: {e}")
    except ZeroDivisionError as e:
        st.error(f"연산 오류: {e}")
    except Exception as e:
        st.error(f"알 수 없는 오류: {e}")
