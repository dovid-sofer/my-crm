import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרת כותרת ועיצוב
st.set_page_config(page_title="CRM תורמים - מערכת ניהול", layout="wide")

# פונקציה לניקוי סכומים (הופכת "₪ 100" למספר 100)
def clean_currency(value):
    if pd.isna(value) or value == "": return 0
    if isinstance(value, str):
        value = value.replace('₪', '').replace('$', '').replace(',', '').strip()
        try:
            return float(value.split()[0]) # לוקח רק את המספר הראשון במקרה של הערות
        except:
            return 0
    return value

# טעינת הנתונים (כאן תדביק את הקישור לגוגל שיטס שלך בהמשך)
@st.cache_data
def load_data():
    # בשלב ראשון נשתמש בדוגמה, אחרי שתעלה נחבר את זה ל-Google Sheets
    df = pd.read_clipboard() # זמני לצורך הבדיקה שלך
    return df

# --- ממשק האתר ---
st.title("🎯 מערכת CRM לניהול תורמים")

# סיסמה פשוטה
password = st.sidebar.text_input("הכנס סיסמה", type="password")
if password == "1234": # שנה כאן את הסיסמה שלך
    
    df = load_data()
    
    # זיהוי עמודות הקמפיינים (כל מה שלא פרטים אישיים)
    personal_cols = ['משפחה', 'פרטי', 'רחוב', 'טלפון', 'טלפון נוסף', 'קהילה']
    campaign_cols = [c for c in df.columns if c not in personal_cols]

    # --- תפריט צד ---
    menu = st.sidebar.selectbox("תפריט", ["סטטיסטיקה", "כרטיס תורם", "הוספת תורם"])

    if menu == "סטטיסטיקה":
        st.header("📊 ניתוח קמפיינים")
        
        # בחירת קמפיין להשוואה
        selected_holiday = st.selectbox("בחר חג לניתוח", ["פסח", "פורים", "ר''ה", "חנוכה"])
        
        # חישוב סכומים לפי שנים
        holiday_data = []
        for col in campaign_cols:
            if selected_holiday in col:
                year = col.replace(selected_holiday, "").strip()
                total = df[col].apply(clean_currency).sum()
                holiday_data.append({"שנה": year, "סכום": total})
        
        stats_df = pd.DataFrame(holiday_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"סה''כ גיוס - {selected_holiday}")
            fig = px.bar(stats_df, x="שנה", y="סכום", color="שנה", text_auto=True)
            st.plotly_chart(fig)
        
        with col2:
            current_total = stats_df.iloc[-1]['סכום'] if not stats_df.empty else 0
            prev_total = stats_df.iloc[-2]['סכום'] if len(stats_df) > 1 else 0
            diff = current_total - prev_total
            st.metric("קמפיין נוכחי", f"₪{current_total:,.0f}", delta=f"{diff:,.0f}")

    elif menu == "כרטיס תורם":
        st.header("👤 חיפוש וכרטיס תורם")
        
        df['Full_Name'] = df['משפחה'] + " " + df['פרטי']
        donor_name = st.selectbox("בחר תורם", df['Full_Name'].unique())
        
        donor_info = df[df['Full_Name'] == donor_name].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        col1.write(f"**טלפון:** {donor_info['טלפון']}")
        col2.write(f"**כתובת:** {donor_info['רחוב']}")
        col3.write(f"**קהילה:** {donor_info['קהילה']}")
        
        st.divider()
        
        # כפתורי סינון חגים
        h_col1, h_col2, h_col3, h_col4 = st.columns(4)
        show_all = h_col1.button("הצג הכל")
        show_passover = h_col2.button("פסח בלבד")
        show_purim = h_col3.button("פורים בלבד")
        
        # הצגת היסטוריית תרומות
        history = []
        for col in campaign_cols:
            val = donor_info[col]
            if pd.notna(val) and val != "":
                history.append({"קמפיין": col, "סכום": val})
        
        hist_df = pd.DataFrame(history)
        
        if show_passover:
            hist_df = hist_df[hist_df['קמפיין'].str.contains("פסח")]
        elif show_purim:
            hist_df = hist_df[hist_df['קמפיין'].str.contains("פורים")]
            
        st.table(hist_df)

    elif menu == "הוספת תורם":
        st.header("➕ הוספת תורם חדש למערכת")
        with st.form("new_donor"):
            f1, f2 = st.columns(2)
            new_last = f1.text_input("שם משפחה")
            new_first = f2.text_input("שם פרטי")
            new_phone = f1.text_input("טלפון")
            new_addr = f2.text_input("כתובת")
            submit = st.form_submit_button("שמור תורם")
            if submit:
                st.success(f"התורם {new_first} {new_last} נוסף בהצלחה!")

else:
    st.warning("אנא הכנס סיסמה בתפריט הצד")
