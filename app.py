import math
import streamlit as st

# ---------------------------------------------------------
# 1. 페이지 설정 및 세션 상태 초기화
# ---------------------------------------------------------
st.set_page_config(page_title="약물 용출 실험 정리 앱", layout="wide")

# [수행평가 조건 1: 리스트] 여러 실험과 용출률 데이터를 담는 빈 리스트([]) 생성
if 'saved_experiments' not in st.session_state:
    st.session_state['saved_experiments'] = []

if 'current_rates' not in st.session_state:
    st.session_state['current_rates'] = []

if 'show_result' not in st.session_state:
    st.session_state['show_result'] = False

if 'drug_name_input' not in st.session_state:
    st.session_state['drug_name_input'] = ""


# ---------------------------------------------------------
# 2. 사용자 정의 함수(def) 영역
# ---------------------------------------------------------
# [수행평가 조건 2: 함수 def] 현재 입력 중인 실험을 초기화하는 함수
def reset_current_experiment():
    st.session_state['current_rates'] = []
    st.session_state['show_result'] = False
    st.session_state['drug_name_input'] = ""


# [수행평가 조건 2: 함수 def] 실험 결과를 저장하고 입력창을 비우는 함수
def save_and_reset_experiment(drug_name, time_interval, times, rates, finish_time):
    experiment_record = {
        "id": len(st.session_state.get('saved_experiments', [])) + 1, # 리스트 함수 len()
        "drug_name": drug_name,
        "interval": time_interval,
        "times": list(times), # 리스트 함수 list()
        "rates": list(rates),
        "finish_time": finish_time
    }
    # [수행평가 조건 1: 리스트 함수] .append()를 사용해 리스트에 새 실험 추가
    st.session_state['saved_experiments'].append(experiment_record)
    reset_current_experiment()


# [수행평가 조건 2: 함수 def] 시간과 용출률 리스트를 차트 데이터로 변환하는 함수
def create_chart_data(times, rates, col_name="용출률(%)"):
    chart_data = []
    # [수행평가 조건 4: 반복문 for] 리스트 길이(len)만큼 반복하며 데이터 짝짓기
    for i in range(len(times)):
        chart_data.append({"시간(분)": times[i], col_name: rates[i]})
    return chart_data


# [수행평가 조건 2: 함수 def] 특정 시간(t분)의 용출률을 추정하는 보조 함수 (선형 보간)
def get_rate_at_time(exp, target_time):
    times = exp['times']
    rates = exp['rates']
    
    # [수행평가 조건 3: 조건문 if-elif-else]
    if target_time <= 0:
        return 0.0
    elif target_time >= times[-1]:
        return 100.0
    
    # 0분부터 시작하는 전체 시간/용출률 리스트 구성
    full_times = [0] + times
    full_rates = [0.0] + rates
    
    # [수행평가 조건 4: 반복문 for] target_time이 속한 구간 찾기
    for i in range(len(full_times) - 1):
        t1, t2 = full_times[i], full_times[i + 1]
        r1, r2 = full_rates[i], full_rates[i + 1]
        if t1 <= target_time <= t2:
            # 두 시간 사이의 비율만큼 용출률 계산
            ratio = (target_time - t1) / (t2 - t1)
            return r1 + (r2 - r1) * ratio
    return 100.0


# [수행평가 조건 2: 함수 def] 시간 단위가 같든 다르든 평균 시간과 평균 용출률을 계산하는 함수
def calculate_averages(selected_list):
    total_finish_time = 0
    max_finish_time = 0
    interval_list = []
    
    # [수행평가 조건 4: 반복문 for] 완료 시간 합산 및 각 실험의 시간 단위 수집
    for exp in selected_list:
        total_finish_time += exp['finish_time']
        if exp['finish_time'] > max_finish_time:
            max_finish_time = exp['finish_time']
        interval_list.append(exp['interval'])
            
    avg_finish_time = total_finish_time / len(selected_list)
    
    # 선택된 시간 단위들의 최대공약수를 공통 비교 시간 간격으로 계산
    common_interval = interval_list[0]
    for iv in interval_list[1:]:
        common_interval = math.gcd(common_interval, iv)
        
    common_times = []
    avg_rates = []
    
    # [수행평가 조건 4: 반복문 for] 공통 시간 간격마다 모든 실험의 평균 용출률 계산
    for t in range(common_interval, max_finish_time + common_interval, common_interval):
        step_sum = 0
        for exp in selected_list:
            step_sum += get_rate_at_time(exp, t)
        common_times.append(t)
        avg_rates.append(round(step_sum / len(selected_list), 2))
        
    return round(avg_finish_time, 1), common_times, avg_rates, common_interval


# ---------------------------------------------------------
# 3. 메인 화면 UI 구성
# ---------------------------------------------------------
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
    
    rates = st.session_state.get('current_rates', [])
    current_step = len(rates) + 1 # 리스트 함수 len()
    current_time = current_step * time_interval

    # [수행평가 조건 3: 조건문 if-else] 아직 100%에 도달하지 않았으면 입력창 표시, 100%면 종료 안내
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
                # [수행평가 조건 3: 조건문 if-else] 이전 용출률보다 작은 값 입력 방지
                if rates and new_rate < rates[-1]:
                    st.warning(f"이전 용출률({rates[-1]}%)보다 작을 수 없습니다!")
                else:
                    # [수행평가 조건 1: 리스트 함수] .append()로 입력한 용출률 추가
                    st.session_
