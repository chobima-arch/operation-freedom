import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- ページ基本設定 ---
st.set_page_config(page_title="Operation Freedom", page_icon="🏯", layout="wide")

# --- 軍師のタイトルコール ---
st.title("🏯 Operation Freedom 特設デジタル作戦盤")
st.caption("総司令官専用・iPad最適化Webダッシュボード（G20対応型）")

st.markdown("""
> **軍師報告：** 本日の資産状況や今後の追撃ペースを入力してくださいだだにゆ。
> 65歳時点の野村要塞の総戦闘力、および73歳以降のSlow12（S12）フェーズにいたるまでのローン残高推移を動的に算出しますだだにゆ！ニヤリｗ
""")

# --- サイドバー：前線のリアルタイム・パラメータ入力 ---
st.sidebar.header("⚔️ 前線アセット現在値（動的入力）")

# 1. 特定口座パラメータ
st.sidebar.subheader("① 旧・特定口座部隊")
current_tokutei = st.sidebar.number_input("現在の評価額（万円）", value=1800, step=50)
monthly_tokutei = st.sidebar.slider("毎月の追撃額（万円/月）", 0, 50, 30)

# 2. DCパラメータ
st.sidebar.subheader("② 企業型DC部隊")
current_dc = st.sidebar.number_input("DC現在の総額（万円）", value=3400, step=50)
monthly_dc = st.sidebar.slider("60歳までの追撃額（万円/月）", 0.0, 10.0, 5.5, step=0.5)

# 3. NISAパラメータ
st.sidebar.subheader("③ SBI聖域（NISA）")
current_nisa = st.sidebar.number_input("NISA現在の評価額（万円）", value=1550, step=50)
remain_nisa_investment = st.sidebar.number_input("残り2年の総追撃額（万円）", value=720, step=10)

# 4. 共通システムパラメータ
st.sidebar.subheader("⚙️ 巡航システム設定")
target_yield = st.sidebar.slider("想定運用利回り（年利 %）", 1.0, 15.0, 7.0, step=0.5) / 100
annual_loan_draw = st.sidebar.slider("65歳以降のローン生活費（万円/年）", 300, 1200, 720, step=10)
s12_loan_ratio = st.sidebar.slider("73歳（S12）以降の生活費縮小率（%）", 10, 100, 50) / 100

# --- シミュレーション・ロジックコア ---
age_start = 53
age_retire = 65
age_s12 = 73
age_end = 85

years_to_retire = age_retire - age_start # 12年間

# 65歳時点の特定口座の計算（月利複利）
tokutei_val = current_tokutei
for m in range(years_to_retire * 12):
    tokutei_val = (tokutei_val + monthly_tokutei) * (1 + target_yield / 12)

# 65歳時点のDCの計算（60歳まで積立、その後5年一括運用）
dc_val = current_dc
for m in range(12 * 12):
    current_age = age_start + (m // 12)
    # 60歳までは追撃あり、それ以降は一括運用のみ
    if current_age < 60:
        dc_val = (dc_val + monthly_dc) * (1 + target_yield / 12)
    else:
        dc_val = dc_val * (1 + target_yield / 12)

# 65歳時点のNISAの計算（2年追撃、その後10年一括運用）
nisa_val = current_nisa
for m in range(years_to_retire * 12):
    if m < 24: # 最初の2年で枠埋め
        nisa_val = (nisa_val + (remain_nisa_investment / 24)) * (1 + target_yield / 12)
    else:
        nisa_val = nisa_val * (1 + target_yield / 12)

# 野村純担保総額
nomura_fortress = tokutei_val + dc_val

# --- 画面表示：メインメトリクスボード ---
st.header("🏆 65歳遷都の瞬間・予測戦闘力（年利7%ベース軸）")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🏯 野村要塞（純担保総額）", f"{int(nomura_fortress):,} 万円")
with col2:
    st.metric("① 旧・特定口座", f"{int(tokutei_val):,} 万円")
with col3:
    st.metric("② 企業型DC（再配備）", f"{int(dc_val):,} 万円")
with col4:
    st.metric("🛡️ SBI聖域（NISA総額）", f"{int(nisa_val):,} 万円")

st.divider()

# --- 後半戦シミュレーション（65歳〜85歳の20年間：G20） ---
ages = list(range(65, 86))
nomura_assets = []
nisa_assets = []
loan_balances = []
leverage_ratios = []

current_nomura = nomura_fortress
current_nisa = nisa_val
current_loan = 0.0

for age in ages:
    nomura_assets.append(current_nomura)
    nisa_assets.append(current_nisa)
    loan_balances.append(current_loan)
    
    # レバレッジ比率計算
    lev = (current_loan / current_nomura) * 100 if current_nomura > 0 else 0
    leverage_ratios.append(lev)
    
    # ローン引き出し額の決定（A8かS12か）
    if age < age_s12:
        draw = annual_loan_draw
    else:
        draw = annual_loan_draw * s12_loan_ratio
        
    # 次の年への遷移（年利7%運用とローンの追加）
    current_nomura = (current_nomura) * (1 + target_yield)
    current_nisa = current_nisa * (1 + target_yield)
    # ローン残高（金利は仮に年2.0%と想定して累積、生活費が加算される）
    if age < age_end:
        current_loan = (current_loan + draw) * 1.02 

# データフレーム化
df_g20 = pd.DataFrame({
    "年齢": ages,
    "野村要塞資産": nomura_assets,
    "SBI・NISA聖域": nisa_assets,
    "ローン借入残高": loan_balances,
    "レバレッジ比率(%)": leverage_ratios
})

# --- グラフィカル作戦盤（チャート表示） ---
st.header("📈 G20フェーズ（65歳〜85歳）資産・ローン動的推移マップ")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_g20["年齢"], y=df_g20["野村要塞資産"], name="🏯 野村要塞資産(担保)", line=dict(color='#1f77b4', width=3)))
fig.add_trace(go.Scatter(x=df_g20["SBI・NISA聖域"], x=df_g20["年齢"], y=df_g20["SBI・NISA聖域"], name="🛡️ SBI・NISA聖域(無税)", line=dict(color='#2ca02c', width=2, dash='dash')))
fig.add_trace(go.Scatter(x=df_g20["年齢"], y=df_g20["ローン借入残高"], name="🚨 ローン借入残高", line=dict(color='#d62728', width=3)))

fig.update_layout(title="資産増殖 vs ローン残高のデッドヒート", xlab_title="年齢", ylab_title="金額（万円）", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# --- 動的AI（軍師）アドバイスシステム ---
st.header("🧠 専属軍師のリアルタイム動的進言")

latest_lev = leverage_ratios[0] # 65歳時点
max_lev = max(leverage_ratios)
end_asset = nomura_assets[-1] + nisa_assets[-1]

col_adv1, col_adv2 = st.columns(2)

with col_adv1:
    st.subheader("📊 陣形の健康度チェック")
    st.write(f"* **G20期間中の最大レバレッジ比率:** {max_lev:.1f} %")
    st.write(f"* **85歳時点の持株会抜き総戦闘力:** {int(end_asset):,} 万円")
    
    # レバレッジ比率に応じた動的アラート
    if max_lev < 25:
        st.success("🟢 【絶対不沈モード】レバレッジが25%未満に抑え込まれています！暴落耐性-50%超。核シェルター級の安全性だだにゆ！")
    elif max_lev <= 35:
        st.info("🔵 【巡航強化モード】司令官のコア戦略である資産の35%借入圏内だだにゆ！暴落時は裏のNISAバッファ発動の準備を怠るなだだにゆ！")
    else:
        st.warning("🔴 【攻撃特化モード】レバレッジが35%を超えています！株価の日々チェックと、SBIのNISA防衛部隊の即時注入ルートを確認してくださいだだにゆ！")

with col_adv2:
    st.subheader("💬 軍師の直言")
    if nomura_fortress >= 20000:
        st.markdown(f"""
        「総司令官！！！ 現在の入力データから算出された65歳時の純担保は **{int(nomura_fortress/10000)}億円** を突破しているだだにゆ！ 
        これなら毎月60万円（年間720万）のローンなど、増殖する果実の数分の一を削るに過ぎないだだにゆね。
        73歳からのS12で生活費を **{int(s12_loan_ratio*100)}%** に落とす計画も相まって、資産の拡大スピードが借金の累積スピードに完全勝利しているだだにゆ！ 大勝利のニヤリだだにゆ！ｗｗ」
        """)
    else:
        st.markdown("""
        「総司令官！ 65歳時点の純担保が2億円を下回るシミュレーションになっているだだにゆ。
        この場合は、現役時代の追撃スピード（特定口座への月30万やDCなど）を少しだけ強めるか、利回りの上振れを狙う精鋭銘柄への集中投資を検討すると、一気に2億円の大大要塞へ復帰できるだだにゆ！！」
        """)

# データテーブル表示（確認用）
if st.checkbox("🔍 詳細な数値データ一覧（グリッド表示）"):
    st.dataframe(df_g20.style.format({
        "野村要塞資産": "{:,.0f}万円",
        "SBI・NISA聖域": "{:,.0f}万円",
        "ローン借入残高": "{:,.0f}万円",
        "レバレッジ比率(%)": "{:.2f}%"
    }))
