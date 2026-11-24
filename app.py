import math
import streamlit as st

# ---------------------------------------------------------
# 1. 페이지 설정 및 세션 상태 초기화
# ---------------------------------------------------------
st.set_page_config(page_title="약물 용출 실험 정리 앱", layout="wide")

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
def reset_current_experiment():
    st.session_state['current_rates'] = []
    st.session_state['show_result'] = False
    st.session_state['drug_name_input'] = ""


def save_and_reset_experiment(drug_name, time_interval, times, rates, finish_time):
    experiment_record = {
        "id": len(st.session_state.get('saved_experiments', [])) + 1,
        "drug_name": drug_name,
        "interval": time_interval,
        "times": list(times),
        "rates": list(rates),
        "finish_time": finish_time
    }
    st.session_state['saved_experiments'].append(experiment_record)
    reset_current_experiment()


def create_chart_data(times, rates, col_name="용출률(%)"):
    chart_data = []
    for i in range(len(times)):
        chart_data.append({"시간(분)": times[i], col_name: rates[i]})
    return chart_data


def get_rate_at_time(exp, target_time):
    times = exp['times']
    rates = exp['rates']
    
    if target_time <= 0:
        return 0.0
    elif target_time >= times[-1]:
        return 100.0
    
    full_times = [0] + times
    full_rates = [0.0] + rates
    
    for i in range(len(full_times) - 1):
        t1, t2 = full_times[i], full_times[i + 1]
        r1, r2 = full_rates[i], full_rates[i + 1]
        if t1 <= target_time <= t2:
            ratio = (target_time - t1) / (t2 - t1)
            return r1 + (r2 - r1) * ratio
    return 100.0


def calculate_averages(selected_list):
    total_finish_time = 0
    max_finish_time = 0
    interval_list = []
    
    for exp in selected_list:
        total_finish_time += exp['finish_time']
        if exp['finish_time'] > max_finish_time:
            max_finish_time = exp['finish_time']
        interval_list.append(exp['interval'])
            
    avg_finish_time = total_finish_time / len(selected_list)
    
    common_interval = interval_list[0]
    for iv in interval_list[1:]:
        common_interval = math.gcd(common_interval, iv)
        
    common_times = []
    avg_rates = []
    
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
                    st.session_state['current_rates'].append(new_rate)
                    st.rerun()
    else:
        st.success(f"🎉 **{current_time - time_interval}분** 만에 100% 용출이 완료되었습니다! 아래 버튼을 눌러 결과를 확인하세요.")

    if rates:
        st.write("**현재 입력된 기록:**", [f"{(i+1)*time_interval}분: {r}%" for i, r in enumerate(rates)])

    st.divider()

    if st.button("📊 한눈에 보기", type="primary", use_container_width=True):
        if not drug_name.strip():
            st.error("⚠️ 약물 이름을 먼저 입력해주세요!")
        elif not rates or rates[-1] < 100.0:
            st.error("⚠️ 100% 용출이 완료될 때까지 데이터를 모두 입력해주세요!")
        else:
            st.session_state['show_result'] = True

    if st.session_state.get('show_result', False) and rates and rates[-1] == 100.0:
        st.markdown("---")
        st.header(f"📌 {drug_name} 용출 실험")
        
        times = [(i + 1) * time_interval for i in range(len(rates))]
        finish_time = times[-1]
        
        chart_data = create_chart_data(times, rates, f"{drug_name} 용출률(%)")
        st.line_chart(chart_data, x="시간(분)", y=f"{drug_name} 용출률(%)")
        
        st.success(f"⏱️ **100% 용출 완료까지 총 {finish_time}분 걸렸습니다.**")
        
        st.write("📋 **시간 단위별 상세 용출률:**")
        for i in range(len(times)):
            st.write(f"- **{times[i]}분**: {rates[i]}% 용출")
            
        st.write("")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("💾 실험데이터저장", type="secondary", use_container_width=True):
                experiment_record = {
                    "id": len(st.session_state.get('saved_experiments', [])) + 1,
                    "drug_name": drug_name,
                    "interval": time_interval,
                    "times": list(times),
                    "rates": list(rates),
                    "finish_time": finish_time
                }
                st.session_state['saved_experiments'].append(experiment_record)
                st.toast(f"'{drug_name}' 실험 데이터가 저장소에 저장되었습니다!", icon="✅")
                
        with btn_col2:
            st.button(
                "💾 저장하고 새 실험 쓰기", 
                type="primary", 
                use_container_width=True,
                on_click=save_and_reset_experiment,
                args=(drug_name, time_interval, times, rates, finish_time)
            )

with tab2:
    st.subheader("🗄️ 저장된 실험 데이터 목록")
    
    saved_list = st.session_state.get('saved_experiments', [])
    
    if not saved_list:
        st.info("아직 저장된 실험 데이터가 없습니다. 첫 번째 탭에서 실험을 완료하고 저장해주세요.")
    else:
        st.write(f"총 **{len(saved_list)}개**의 실험 데이터가 저장되어 있습니다.")
        
        options = []
        for exp in saved
