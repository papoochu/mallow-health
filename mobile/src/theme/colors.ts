import {
  Platform,
  StyleSheet,
} from "react-native";


export type ThemeColors = {
  background: string;
  surface: string;
  surfaceSoft: string;
  text: string;
  textMuted: string;
  heading: string;
  border: string;
  accent: string;
  accentSoft: string;
  good: string;
  goodSoft: string;
  warning: string;
  warningSoft: string;
  pink: string;
  pinkSoft: string;
  chartLine: string;
  chartMuted: string;
  input: string;
  inputText: string;
};


export const lightColors: ThemeColors = {
  background: "#F8F5F0",
  surface: "#FFFFFF",
  surfaceSoft: "#F0F4EE",
  text: "#3E4741",
  textMuted: "#7B877E",
  heading: "#536B5A",
  border: "#E6DED5",
  accent: "#6E8C76",
  accentSoft: "#E7F0E9",
  good: "#63856D",
  goodSoft: "#EDF5EF",
  warning: "#8B7852",
  warningSoft: "#F4EEDF",
  pink: "#9C7388",
  pinkSoft: "#F2E8EE",
  chartLine: "#6F8F78",
  chartMuted: "#D9D5D0",
  input: "#566B5D",
  inputText: "#FFFFFF",
};


export const darkColors: ThemeColors = {
  background: "#171C18",
  surface: "#202720",
  surfaceSoft: "#253128",
  text: "#E8EEE9",
  textMuted: "#98A69B",
  heading: "#C1D7C5",
  border: "#344238",
  accent: "#A5C4AA",
  accentSoft: "#27362B",
  good: "#AED0B6",
  goodSoft: "#27362B",
  warning: "#D8C597",
  warningSoft: "#3A3426",
  pink: "#D4B9C8",
  pinkSoft: "#342A31",
  chartLine: "#A5C4AA",
  chartMuted: "#46564A",
  input: "#202720",
  inputText: "#FFFFFF",
};


export function createAppStyles(
  colors: ThemeColors,
) {
  return StyleSheet.create(
    {
      root: {
        backgroundColor: colors.background,
        flex: 1,
      },

      screenArea: {
        flex: 1,
      },

      bottomBar: {
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderTopWidth: 1,
        bottom: 0,
        flexDirection: "row",
        left: 0,
        paddingBottom: (
          Platform.OS === "ios"
            ? 18
            : 8
        ),
        position: "absolute",
        right: 0,
      },
    }
  );
}
