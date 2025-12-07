# **London Bleeds: Style Guide & Design Tokens**

## **1\. Overview**

This document outlines the visual language and design system for "London Bleeds: The Whitechapel Diaries." The aesthetic is grounded in a "Gothic Realism" tone—evoking the fog, tension, and moral ambiguity of 1888 London while maintaining modern readability.

## **2\. Color Palette (Light Mode)**

### **Primary Brand Colors**

* **Primary (\#293351):** Navy. Used for headings, main UI elements, and body text.  
* **Accent** (\#CD7B00): Orange. Used for character names, location icons, interactive elements, and highlighting key information.  
* **Background (\#FDF9F5):** Warm Off-White. The main canvas color, mimicking paper or parchment.

### **Secondary & Utility Colors**

* **Muted (\#929DBF):** Muted Blue/Grey. Used for secondary text and borders.  
* **Muted Foreground (\#677398):** Darker Muted Blue. Used for less prominent text.  
* **Border (\#C5CBDD):** Light Grey-Blue. Default border color.

### **Dark Mode (Reference)**

* **Primary:** \#ffe7d6 (Cream)  
* **Accent:** \#f06906 (Bright Orange)  
* **Background:** \#363636 (Dark Gray)  
* **Muted:** \#9f8a7f (Muted Brown)

## **3\. Typography**

### **Font Families**

* **Headings:** Playfair Display (Serif)  
  * *Usage:* Titles, location headers, act names.  
* **Body:** Open Sans (Sans-Serif)  
  * *Usage:* Narrative text, UI labels, inventory items.  
* **Handwriting (Optional/Journal):** Patrick Hand or Caveat (Cursive)  
  * *Usage:* Watson's journal entries, handwritten notes.

### **Font Sizes & Scale (Responsive)**

* **Title:**  
  * Desktop: 76px  
  * Tablet: 58px  
  * Mobile: 42px  
* **Subtitle:**  
  * Desktop: 48px  
  * Tablet: 40px  
  * Mobile: 32px  
* **Heading:**  
  * Desktop: 28.7px  
  * Tablet: 26px  
  * Mobile: 24px  
* **Body / Input:**  
  * Desktop: 20px  
  * Tablet: 18px  
  * Mobile: 16px

### **Font Weights**

* **Light:** 300  
* **Regular:** 400  
* **Medium:** 500  
* **Bold:** 700  
* **Extra Bold:** 800

### **Line Heights**

* **Body:** 1.8 (approx. 36px on desktop) or 30px depending on density.  
* **Headings:** \~1.2 or specific pixel values (e.g., 28.7px).

## **4\. Spacing & Layout**

### **Grid System**

* **Base Unit:** 4px  
* **Scale:**  
  * 1: 4px  
  * 2: 8px  
  * 3: 12px  
  * 4: 16px  
  * 5: 20px  
  * 6: 24px  
  * 8: 32px

### **Breakpoints**

* **Mobile:** 0px \- 768px  
* **Tablet:** 768px \- 1024px  
* **Desktop:** 1024px+

### **Container Widths**

* **Max** Content **Width:** 896px (max-w-4xl) or 65ch for optimal reading measure.

## **5\. UI Elements**

### **Borders & Radius**

* **Default Radius:** 19.14px (Rounded-lg/xl)  
* **Thin Width:** 1.2px  
* **Accent Width:** 2px

### **Interactive States**

* **Clickable/Link:** Highlighted in Accent Color (\#CD7B00) or Primary with underline.  
* **Focus:** Accent color ring or border.

### **Narrative Text Formatting**

* **Standard Text:** Primary Color (\#293351).  
* **Character Names:** **Bold** in Accent Color (\#CD7B00).  
* **Thoughts:** *Italicized* in Primary Color, often blockquoted.  
* **Key Clues/Objects:** Can be highlighted or bolded.

## **6\. Components (From React Implementation)**

### **Sidebar (Journal/Stats)**

* **Background:** Game Background (\#FDF9F5)  
* **Border:** Right border in Border Color (\#C5CBDD)  
* **Font:** Handwritting style for notes.

### **Input Area**

* **Location:** Fixed at bottom.  
* **Style:** Clean, minimal, floating above background gradient.  
* **Button:** Icon-only (Send) or Text+Icon (Consult Holmes).

### **Game Feed**

* **Scroll:** Smooth scrolling.  
* **Animation:** Fade-in for new text blocks.  
* **Separation:** Gener