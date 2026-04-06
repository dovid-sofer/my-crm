import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="והשיב - CRM", layout="wide")

# עיצוב נדרים פלוס
st.markdown("""
    <style>
    .main { background-color: #f4f7f7; }
    .stHeader { background-color: #00b5ad; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .donor-card { background-color: white; padding: 25px; border-radius: 15px; border-right: 8px solid #00b5ad; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .stat-box { background-color: #e0f7f6; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #00b5ad; }
    h1, h2, h3 { color: #007a75; }
    </style>
    """, unsafe_allow_html=True)

def clean_currency(value):
    if pd.isna(value) or str(value).strip() in ["", " ", "0", "nan"]: return 0
    if isinstance(value, str):
        value = value.replace('₪', '').replace('$', '').replace(',', '').strip()
        try: return float(value.split()[0])
        except: return 0
    return value

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('donors.csv', encoding='utf-8-sig')
    except:
        df = pd.read_csv('donors.csv', encoding='cp1255')
    df.columns = [c.strip() for c in df.columns]
    return df

# כותרת
st.markdown('<div class="stHeader"><h1 style="color:white; text-align:center; margin:0;">🎯 והשיב - ניהול תורמים וקמפיינים</h1></div>', unsafe_allow_html=True)

password = st.sidebar.text_input("הכנס סיסמה", type="password")
if password == "dudi330582008":
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    
    df = st.session_state.data
    personal_cols = ['משפחה', 'פרטי', 'רחוב', 'טלפון', 'טלפון נוסף', 'קהילה']
    campaign_cols = [c for c in df.columns if c not in personal_cols and "Full_Name" not in c]
    df['Full_Name'] = df['משפחה'].fillna('') + " " + df['פרטי'].fillna('')

    menu = st.sidebar.radio("תפריט", ["🏠 כרטיס תורם", "📊 סטטיסטיקה כללית"])

    if menu == "🏠 כרטיס תורם":
        donor_name = st.selectbox("חפש תורם:", ["חפש שם..."] + list(df['Full_Name'].unique()))
        
        if donor_name != "חפש שם...":
            idx = df[df['Full_Name'] == donor_name].index[0]
            donor_info = df.loc[idx]
            
            # הצגת כרטיס
            st.markdown(f"""
            <div class="donor-card">
                <h2 style="margin:0;">👤 {donor_name}</h2>
                <hr>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                    <p>📞 <b>טלפון:</b> {donor_info['טלפון'] if pd.notna(donor_info['טלפון']) else '---'}</p>
                    <p>🏠 <b>כתובת:</b> {donor_info['רחוב'] if pd.notna(donor_info['רחוב']) else '---'}</p>
                    <p>🏘️ <b>קהילה:</b> {donor_info['קהילה'] if pd.notna(donor_info['קהילה']) else '---'}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # כפתור עריכה
            edit_mode = st.toggle("✏️ מצב עריכה (הוספת תרומות ושינוי פרטים)")

            if edit_mode:
                st.info("כעת ניתן לשנות נתונים ישירות בטבלה. בסיום, הורד את הקובץ המעודכן.")
                # עריכת פרטים אישיים
                edited_personal = st.data_editor(df.loc[[idx], personal_cols], key="personal_edit")
                # עריכת תרומות
                history_cols = campaign_cols
                edited_history = st.data_editor(df.loc[[idx], history_cols], key="history_edit")
                
                if st.button("💾 עדכן בזיכרון האתר"):
                    df.loc[idx, personal_cols] = edited_personal.iloc[0]
                    df.loc[idx, history_cols] = edited_history.iloc[0]
                    st.session_state.data = df
                    st.success("הנתונים עודכנו זמנית באתר!")
                    
                # אפשרות להורדת הקובץ כדי לשמור באמת
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 הורד קובץ CSV מעודכן לגיבוי", csv, "donors_updated.csv", "text/csv")

            else:
                # תצוגה רגילה (סטייל נדרים)
                total_sum = sum([clean_currency(donor_info[c]) for c in campaign_cols])
                
                col1, col2, col3 = st.columns(3)
                col1.markdown(f'<div class="stat-box"><h4>סה"כ תרומות</h4><h2>₪{total_sum:,.0f}</h2></div>', unsafe_allow_html=True)
                
                st.write("### 📋 היסטוריית תרומות")
                filter_h = st.radio("סנן לפי חג:", ["הכל", "פסח", "פורים", "ר''ה", "חנוכה"], horizontal=True)
                
                history = []
                for col in campaign_cols:
                    val = donor_info[col]
                    if pd.notna(val) and str(val).strip() not in ["", "nan"]:
                        if filter_h == "הכל" or filter_h in col:
                            history.append({"קמפיין": col, "סכום": val})
                
                if history:
                    st.dataframe(pd.DataFrame(history), use_container_width=True)
                else:
                    st.write("אין נתונים רשומים.")

    elif menu == "📊 סטטיסטיקה כללית":
        st.subheader("ניתוח הכנסות לפי חגים")
        holiday = st.selectbox("בחר חג:", ["פסח", "פורים", "ר''ה", "חנוכה"])
        
        stats = []
        for col in campaign_cols:
            if holiday in col:
                total = df[col].apply(clean_currency).sum()
                stats.append({"קמפיין": col, "סה''כ": total})
        
        if stats:
            fig = px.bar(pd.DataFrame(stats), x="קמפיין", y="סה''כ", color_discrete_sequence=['#00b5ad'])
            st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("אנא הכנס סיסמה")
