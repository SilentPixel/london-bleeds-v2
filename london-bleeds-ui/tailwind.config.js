module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#293351",
        accent: "#CD7B00",
        background: "#FDF9F5",
        muted: "#929DBF",
        border: "#C5CBDD"
      },
      fontFamily: {
        serif: ["Playfair Display", "serif"],
        sans: ["Open Sans", "sans-serif"]
      },
      animation: {
        'in': 'fadeIn 0.3s ease-in-out',
        'slide-in-from-bottom-2': 'slideInFromBottom 0.3s ease-out',
        'slide-in-from-top-4': 'slideInFromTop 0.3s ease-out'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideInFromBottom: {
          '0%': { transform: 'translateY(8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        slideInFromTop: {
          '0%': { transform: 'translateY(-16px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      }
    }
  },
  plugins: [require("@tailwindcss/typography")]
};

