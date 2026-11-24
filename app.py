import streamlit as st

# ---------------------------------------------------------
# 1. 세션 상태 초기화
# ---------------------------------------------------------
if 'saved_experiments' not in st.session_state:
    st.session_state.saved_experiments = []

if 'current_rates' not in st.session_state:
    st.session_state.current_rates = []

if 'show_result' not in st.session_state:
    st.session_state.show_result = False

if 'drug_name_input' not in st.session_state:
    st.session_state.drug_name_input = ""


# ---------------------------------------------------------
# 2. 함수 정의 영역
# ---------------------------------------------------------
def reset_current_experiment():
    """현재 작성 중인 실험 내용을 모두 초기화하는 함수"""
    st.session_state.current_rates = []
    st.session_state.show_result = False
    st.session_state.drug_name_input = ""


def save_and_reset_experiment(drug_name, time_interval, times, rates, finish_time):
    """실험 데이터를 저장하고 즉시 입력 화면을 초기화하는 콜백 함수"""
    experiment_record = {
        "id": len(st.session_state.saved_experiments) + 1,
        "drug_name": drug_name,
        "interval": time_interval,
        "times": times,
        "rates": list(rates),
        "finish_time": finish_time
    }
    st.session_state.saved_experiments.append(experiment_record)
    # 저장 직후 초기화 실행 (콜백 함수 안에서는 에러 없이 정상 작동함)
    reset_current_experiment()


def create_chart_data(times, rates, col_name="용출률(%)"):
    """시간 리스트와 용출률 리스트를 받아 Streamlit 차트용 데이터로 변환하는 함수"""
    chart_data = []
    for i in range(len(times)):
        chart_data.append({"시간(분)": times[i], col_name: rates[i]})
    return chart_data


def calculate_averages(selected_list):
    """선택된 여러 실험 데이터의 평균 완료 시간과 구간별 평균 용출률을 계산하는 함수"""
    total_finish_time = 0
    max_steps = 0
    
    for exp in selected_list:
        total_finish_time += exp['finish_time']
        if len(exp['rates']) > max_steps:
            max_steps = len(exp['rates'])
            
    avg_finish_time = total_finish_time / len(selected_list)
    
    avg_rates = []
    common_times = []
    interval = selected_list[0]['interval']
    
    for step in range(max_steps):
        step_sum = 0
        count = 0
        for exp in selected_list:
            if step < len(exp['rates']):
                step_sum += exp['rates'][step]
            else:
                step_sum += 100.0
            count += 1
            
        avg_rates.append(round(step_sum / count, 2))
        common_times.append((step + 1) * interval)
        
    return round(avg_finish_time, 1), common_times, avg_rates


# ---------------------------------------------------------
# 3. 메인 UI 구성
# ---------------------------------------------------------
st.set_page_config(page_title="약물 용출 실험 정리 앱", layout="wide")
st.title("💊 약물 용출 실험 기록 및 분석 시스템")

tab1, tab2 = st.tabs(["📝 새 실험 기록 및 결과 보기", "📂 저장소 및 반복 실험 평균 분석"])

# =========================================================
# [탭 1] 새 실험 기록 및 한눈에 보기
# =========================================================
with tab1:
    head_col1, head_col2 = st.columns([4, 1])
    with head_col1:
        st.subheader("1. 실험 기본 설정")
    with head_col2:
        st.button("🔄 새 실험 쓰기 (초기화)", on_click=reset_current_experiment, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        drug_name = st.text_input(
            "약물 종류 (이름)를 입력하세요", 
            placeholder="예: 아세트아미노펜 500mg",
            key="drug_name_input"
        )
    with col2:
        time_interval = st.number_input("기록할 시간 단위 (10분 ~ 100분)", min_value=10, max_value=100, value=10, step=5)

    st.divider()
    st.subheader("2. 시간 단위별 용출률(%) 입력")
    
    rates = st.session_state.current_rates
    current_step = len(rates) + 1
    current_time = current_step * time_interval

    if not rates or rates[-1] < 100.0:
        st.info(f"⏱️ 현재 **{current_time}분** 경과 시점의 용출률을 입력하세요. (100% 입력 시 자동 종료)")
        
        input_col1, input_col2 = st.columns([3, 1])
        with input_col1:
            new_rate = st.number_input(
                f"{current_time}분 용출률 (%)", 
                min_value=0.0, 
                max_value=100.0, 
                step=1.0, 
                key=f"rate_input_{current_step}"
            )
        with input_col2:
            st.write("")
            st.write("")
            if st.button("기록 추가", use_container_width=True):
                if rates and new_rate < rates[-1]:
                    st.warning(f"이전 용출률({rates[-1]}%)보다 작을 수 없습니다!")
                else:
                    st.session_state.current_rates.append(new_rate)
                    st.rerun()
    else:
        st.success(f"🎉 **{current_time - time_interval}분** 만에 100% 용출이 완료되었습니다! 아래 버튼을 눌러 결과를 확인하세요.")

    if rates:
        st.write("**현재 입력된 기록:**", [f"{(i+1)*time_interval}분: {r}%" for i, r in enumerate(rates)])

    st.divider()

    # [한눈에 보기] 버튼
    if st.button("📊 한눈에 보기", type="primary", use_container_width=True):
        if not drug_name.strip():
            st.error("⚠️ 약물 이름을 먼저 입력해주세요!")
        elif not rates or rates[-1] < 100.0:
            st.error("⚠️ 100% 용출이 완료될 때까지 데이터를 모두 입력해주세요!")
        else:
            st.session_state.show
