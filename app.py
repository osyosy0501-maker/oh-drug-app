import streamlit as st

# ---------------------------------------------------------
# 1. 세션 상태 초기화 (데이터 영구 저장 공간 역할)
# ---------------------------------------------------------
# 'saved_experiments'는 여러 실험 데이터(딕셔너리)를 담는 '리스트'입니다.
if 'saved_experiments' not in st.session_state:
    st.session_state.saved_experiments = []

if 'current_rates' not in st.session_state:
    st.session_state.current_rates = []

if 'show_result' not in st.session_state:
    st.session_state.show_result = False


# ---------------------------------------------------------
# 2. 함수 정의 영역
# ---------------------------------------------------------
def create_chart_data(times, rates, col_name="용출률(%)"):
    """시간 리스트와 용출률 리스트를 받아 Streamlit 차트용 데이터(리스트 안의 딕셔너리)로 변환하는 함수"""
    chart_data = []
    # 반복문(for)을 사용하여 시간과 용출률을 짝지어 리스트에 추가
    for i in range(len(times)):
        chart_data.append({"시간(분)": times[i], col_name: rates[i]})
    return chart_data


def calculate_averages(selected_list):
    """선택된 여러 실험 데이터(리스트)의 평균 완료 시간과 구간별 평균 용출률을 계산하는 함수"""
    total_finish_time = 0
    max_steps = 0
    
    # 반복문: 총 완료 시간 합산 및 가장 길었던 실험의 단계 수 파악
    for exp in selected_list:
        total_finish_time += exp['finish_time']
        if len(exp['rates']) > max_steps:
            max_steps = len(exp['rates'])
            
    avg_finish_time = total_finish_time / len(selected_list)
    
    # 각 시간 단위(인덱스)별 평균 용출률 계산
    avg_rates = []
    common_times = []
    interval = selected_list[0]['interval'] # 첫 번째 선택 실험의 시간 단위 기준
    
    for step in range(max_steps):
        step_sum = 0
        count = 0
        for exp in selected_list:
            # 해당 실험에 현재 단계(step)의 데이터가 존재하는 경우
            if step < len(exp['rates']):
                step_sum += exp['rates'][step]
            else:
                # 이미 100%에 도달해 일찍 끝난 실험은 100%로 유지하여 평균 계산
                step_sum += 100.0
            count += 1
            
        avg_rates.append(round(step_sum / count, 2))
        common_times.append((step + 1) * interval)
        
    return round(avg_finish_time, 1), common_times, avg_rates


# ---------------------------------------------------------
# 3. 메인 UI 구성 (사이드바 & 탭 분리)
# ---------------------------------------------------------
st.set_page_config(page_title="약물 용출 실험 정리 앱", layout="wide")
st.title("💊 약물 용출 실험 기록 및 분석 시스템")

# 화면을 두 개의 탭으로 분리 (실험 입력 / 저장된 데이터 분석)
tab1, tab2 = st.tabs(["📝 새 실험 기록 및 결과 보기", "📂 저장소 및 반복 실험 평균 분석"])

# =========================================================
# [탭 1] 새 실험 기록 및 한눈에 보기
# =========================================================
with tab1:
    st.subheader("1. 실험 기본 설정")
    col1, col2 = st.columns(2)
    with col1:
        drug_name = st.text_input("약물 종류 (이름)를 입력하세요", placeholder="예: 아세트아미노펜 500mg")
    with col2:
        time_interval = st.number_input("기록할 시간 단위 (10분 ~ 100분)", min_value=10, max_value=100, value=10, step=5)

    st.divider()
    st.subheader("2. 시간 단위별 용출률(%) 입력")
    
    # 현재까지 입력된 데이터 리스트
    rates = st.session_state.current_rates
    current_step = len(rates) + 1
    current_time = current_step * time_interval

    # 조건문(if): 아직 100% 용출에 도달하지 않았을 때만 입력창 표시
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
            st.write("") # 줄맞춤용 여백
            st.write("")
            if st.button("기록 추가", use_container_width=True):
                # 조건문: 이전 단계보다 용출률이 낮아지는 오류 방지
                if rates and new_rate < rates[-1]:
                    st.warning(f"이전 용출률({rates[-1]}%)보다 작을 수 없습니다!")
                else:
                    st.session_state.current_rates.append(new_rate)
                    st.rerun()
    else:
        st.success(f"🎉 **{current_time - time_interval}분** 만에 100% 용출이 완료되었습니다! 아래 버튼을 눌러 결과를 확인하세요.")

    # 현재까지 입력된 기록 미리보기 및 초기화 버튼
    if rates:
        st.write("**현재 입력된 기록:**", [f"{(i+1)*time_interval}분: {r}%" for i, r in enumerate(rates)])
        if st.button("🔄 현재 입력 초기화"):
            st.session_state.current_rates = []
            st.session_state.show_result = False
            st.rerun()

    st.divider()

    # [한눈에 보기] 버튼
    if st.button("📊 한눈에 보기", type="primary", use_container_width=True):
        # 조건문: 약 이름 입력 여부 및 100% 도달 여부 검증
        if not drug_name.strip():
            st.error("⚠️ 약물 이름을 먼저 입력해주세요!")
        elif not rates or rates[-1] < 100.0:
            st.error("⚠️ 100% 용출이 완료될 때까지 데이터를 모두 입력해주세요!")
        else:
            st.session_state.show_result = True

    # [한눈에 보기] 결과 출력 화면
    if st.session_state.show_result and rates and rates[-1] == 100.0:
        st.markdown("---")
        # 요구사항: 큰 글씨로 '~약 용출 실험' 출력
        st.header(f"📌 {drug_name} 용출 실험")
        
        # 시간 리스트 생성 (반복문)
        times = [(i + 1) * time_interval for i in range(len(rates))]
        finish_time = times[-1]
        
        # 그래프 그리기 (함수 호출)
        chart_data = create_chart_data(times, rates, f"{drug_name} 용출률(%)")
        st.line_chart(chart_data, x="시간(분)", y=f"{drug_name} 용출률(%)")
        
        # 텍스트 메시지로 완료 시간 및 단위별 용출률 출력
        st.success(f"⏱️ **100% 용출 완료까지 총 {finish_time}분 걸렸습니다.**")
        
        st.write("📋 **시간 단위별 상세 용출률:**")
        # 반복문을 통해 각 단위마다 몇 퍼센트 용출되었는지 출력
        for i in range(len(times)):
            st.write(f"- **{times[i]}분**: {rates[i]}% 용출")
            
        st.write("")
        # [실험데이터저장] 버튼
        if st.button("💾 실험데이터저장", type="secondary"):
            experiment_record = {
                "id": len(st.session_state.saved_experiments) + 1,
                "drug_name": drug_name,
                "interval": time_interval,
                "times": times,
                "rates": list(rates), # 리스트 복사본 저장
                "finish_time": finish_time
            }
            st.session_state.saved_experiments.append(experiment_record)
            st.toast(f"'{drug_name}' 실험 데이터가 저장소에 성공적으로 저장되었습니다!", icon="✅")


# =========================================================
# [탭 2] 저장된 실험 데이터 공간 및 다중 선택 평균 분석
# =========================================================
with tab2:
    st.subheader("🗄️ 저장된 실험 데이터 목록")
    
    saved_list = st.session_state.saved_experiments
    
    # 조건문: 저장된 데이터가 없는 경우 처리
    if not saved_list:
        st.info("아직 저장된 실험 데이터가 없습니다. 첫 번째 탭에서 실험을 완료하고 저장해주세요.")
    else:
        st.write(f"총 **{len(saved_list)}개**의 실험 데이터가 저장되어 있습니다.")
        
        # 선택할 수 있는 옵션 리스트 생성 (반복문)
        options = []
        for exp in saved_list:
            label = f"[실험 #{exp['id']}] {exp['drug_name']} (단위: {exp['interval']}분 / 완료: {exp['finish_time']}분)"
            options.append(label)
            
        # 여러 실험을 선택할 수 있는 멀티셀렉트 박스
        selected_labels = st.multiselect(
            "비교 및 평균을 계산할 실험들을 선택하세요 (같은 약물의 반복 실험 권장):",
            options=options
        )
        
        # 조건문: 사용자가 1개 이상 선택했을 때 실행
        if selected_labels:
            selected_experiments = []
            # 반복문으로 선택된 라벨에 해당하는 원본 데이터 찾기
            for label in selected_labels:
                idx = options.index(label)
                selected_experiments.append(saved_list[idx])
                
            # 시간 단위가 서로 다른 실험을 섞어서 선택했는지 확인 (조건문)
            intervals = {exp['interval'] for exp in selected_experiments}
            if len(intervals) > 1:
                st.warning("⚠️ 선택한 실험들의 '기록 시간 단위(분)'가 서로 다릅니다. 정확한 단위별 평균을 보려면 같은 시간 단위로 측정한 실험들을 선택해주세요.")
            else:
                st.divider()
                st.header(f"📈 선택된 {len(selected_experiments)}개 실험 통합 분석 결과")
                
                # 함수를 호출하여 평균 완료 시간과 단위별 평균 용출률 계산
                avg_finish, common_times, avg_rates = calculate_averages(selected_experiments)
                
                # 1. 그래프 출력 (평균 용출률 추이)
                avg_chart_data = create_chart_data(common_times, avg_rates, "평균 용출률(%)")
                st.line_chart(avg_chart_data, x="시간(분)", y="평균 용출률(%)")
                
                # 2. 텍스트 메시지로 평균 완료 시간 출력
                st.info(f"⏱️ 선택된 실험들의 100% 용출까지 **평균 {avg_finish}분**이 걸렸습니다.")
                
                # 3. 텍스트 메시지로 단위별 평균 용출률 출력 (반복문)
                st.write("📊 **시간 단위별 평균 용출률:**")
                for i in range(len(common_times)):
                    st.write(f"- **{common_times[i]}분**: 평균 **{avg_rates[i]}%** 용출")
