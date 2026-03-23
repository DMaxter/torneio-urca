import { definePreset } from "@primeuix/themes";
import Aura from "@primeuix/themes/aura";

export const URCATheme = definePreset(Aura, {
  semantic: {
    primary: {
      50: "{orange.50}",
      100: "{orange.100}",
      200: "{orange.200}",
      300: "{orange.300}",
      400: "{orange.400}",
      500: "{orange.500}",
      600: "{orange.600}",
      700: "{orange.700}",
      800: "{orange.800}",
      900: "{orange.900}",
      950: "{orange.950}",
    },
    colorScheme: {
      light: {
        primary: {
          color: "{orange.500}",
          inverseColor: "{surface.0}",
          hoverColor: "{orange.600}",
          activeColor: "{orange.700}",
        },
        highlight: {
          background: "{orange.50}",
          color: "{orange.700}",
        },
        surface: {
          0: "#ffffff",
          50: "#fafaf9",
          100: "#f5f5f4",
          200: "#e7e5e4",
          300: "#d6d3d1",
          400: "#a8a29e",
          500: "#78716c",
          600: "#57534e",
          700: "#44403c",
          800: "#292524",
          900: "#1c1917",
          950: "#0c0a09",
        },
      },
      dark: {
        primary: {
          color: "{orange.400}",
          inverseColor: "{surface.900}",
          hoverColor: "{orange.300}",
          activeColor: "{orange.200}",
        },
        highlight: {
          background: "color-mix(in srgb, {orange.400}, transparent 84%)",
          color: "rgba(255, 255, 255, 0.87)",
        },
        surface: {
          0: "#ffffff",
          50: "#fafaf9",
          100: "#f5f5f4",
          200: "#e7e5e4",
          300: "#d6d3d1",
          400: "#a8a29e",
          500: "#78716c",
          600: "#57534e",
          700: "#44403c",
          800: "#292524",
          900: "#1c1917",
          950: "#0c0a09",
        },
      },
    },
  },
  components: {
    Button: {
      success: {
        background: "#16a34a",
        borderColor: "#16a34a",
        color: "#ffffff",
        hoverBackground: "#15803d",
        hoverBorderColor: "#15803d",
        focusBackground: "#15803d",
      },
      secondary: {
        background: "#ea580c",
        borderColor: "#ea580c",
        color: "#ffffff",
        hoverBackground: "#c2410c",
        hoverBorderColor: "#c2410c",
        focusBackground: "#c2410c",
      },
      danger: {
        background: "#dc2626",
        borderColor: "#dc2626",
        color: "#ffffff",
        hoverBackground: "#b91c1c",
        hoverBorderColor: "#b91c1c",
        focusBackground: "#b91c1c",
      },
    },
  },
});
