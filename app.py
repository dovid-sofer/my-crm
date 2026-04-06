import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CRM תורמים", layout="wide")

# פונקציה לניקוי סכומים - מותאם בדיוק לנתונים שלך
def clean_currency(value):
    if pd.isna(value) or value == "" or value == " ": return 0
    if isinstance(value, str):
        # מנקה סימני שקל, דולר, פסיקים ומילים כמו "לחודש"
        value = value.replace('₪', '').replace('$', '').replace(',', '').replace('₪', '').strip()
        try:
            # לוקח רק את המספר הראשון (למקרה שיש הערות ליד)
            return float(value.split()[0])
        except:
            return 0
    return value

@st.cache_data
def load_data():
    # קריאה עם קידוד שמתאים לעברית (utf-8-sig)
    try:
        df = pd.read_csv('donors.csv', encoding='utf-8-sig')
    except:
        df = pd.read_csv('donors.csv', encoding='cp1255') # ניסיון נוסף לקידוד עברי ישן
    return df

st.title("🎯 מערכת CRM לניהול תורמים")

# סיסמה (תשנה כאן למה שאתה רוצה)
password = st.sidebar.text_input("הכנס סיסמה", type="password")
if password == "dudi330582008": # הסיסמה שרצית
    
    df = load_data()
    
    # עמודות אישיות
    personal_cols = ['משפחה', 'פרטי', 'רחוב', 'טלפון', 'טלפון נוסף', 'קהילה']
    # כל שאר העמודות הן קמפיינים
    campaign_cols = [c for c in df.columns if c not in personal_cols and "Full_Name" not in c]

    menu = st.sidebar.selectbox("תפריט", ["סטטיסטיקה", "כרטיס תורם"])

    if menu == "סטטיסטיקה":
        st.header("📊 ניתוח קמפיינים")
        selected_holiday = st.selectbox("בחר חג לניתוח", ["פסח", "פורים", "ר''ה", "חנוכה"])
        
        holiday_data = []
        for col in campaign_cols:
            if selected_holiday in col:
                total = df[col].apply(clean_currency).sum()
                holiday_data.append({"שנה": col, "סכום": total})
        
        if holiday_data:
            stats_df = pd.DataFrame(holiday_data)
            fig = px.bar(stats_df, x="שנה", y="סכום", text_auto='.2s', title=f"גיוס לפי שנים - {selected_holiday}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("לא נמצאו נתונים לחג שנבחר")

    elif menu == "כרטיס תורם":
        st.header("👤 חיפוש וכרטיס תורם")
        df['Full_Name'] = df['משפחה'].fillna('') + " " + df['פרטי'].fillna('')
        donor_name = st.selectbox("חפש תורם", df['Full_Name'].unique())
        
        donor_info = df[df['Full_Name'] == donor_name].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("משפחה", donor_info['משפחה'])
        c2.metric("טלפון", donor_info['טלפון'])
        c3.metric("קהילה", donor_info['קהילה'])
        
        st.write(f"🏠 **כתובת:** {donor_info['רחוב']}")
        
        st.divider()
        st.subheader("היסטוריית תרומות")
        
        filter_h = st.radio("סנן לפי חג:", ["הכל", "פסח", "פורים", "ר''ה"], horizontal=True)
        
        history = []
        for col in campaign_cols:
            val = donor_info[col]
            if pd.notna(val) and val != "" and val != " ":
                if filter_h == "הכל" or filter_h in col:
                    history.append({"קמפיין": col, "סכום": val})
        
        if history:
            st.table(pd.DataFrame(history))
        else:
            st.write("אין נתונים לתורם זה בסינון הנבחר")

else:
    st.warning("אנא הכנס סיסמה נכונה בתפריט הצד")
