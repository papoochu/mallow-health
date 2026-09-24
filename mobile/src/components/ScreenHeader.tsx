import React from "react";

import {
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  ThemeColors,
} from "../theme/colors";


type ScreenHeaderProps = {
  colors: ThemeColors;
  darkMode: boolean;
  onToggleDarkMode: () => void;
  title?: string;
  subtitle?: string;
};


export default function ScreenHeader({
  colors,
  darkMode,
  onToggleDarkMode,
  title = "Mallow 🌿",
  subtitle = "your gentle personal health companion",
}: ScreenHeaderProps) {
  const styles = createStyles(
    colors
  );

  return (
    <View
      style={styles.headerRow}
    >
      <View
        style={styles.copy}
      >
        <Text
          style={styles.logo}
        >
          {title}
        </Text>

        <Text
          style={styles.subtitle}
        >
          {subtitle}
        </Text>
      </View>

      <Pressable
        onPress={onToggleDarkMode}
        style={styles.themeButton}
      >
        <Text
          style={styles.themeButtonText}
        >
          {
            darkMode
              ? "☀️"
              : "🌙"
          }
        </Text>
      </Pressable>
    </View>
  );
}


function createStyles(
  colors: ThemeColors,
) {
  return StyleSheet.create(
    {
      headerRow: {
        alignItems: "flex-start",
        flexDirection: "row",
        justifyContent: "space-between",
        marginBottom: 18,
      },

      copy: {
        flex: 1,
        paddingRight: 14,
      },

      logo: {
        color: colors.heading,
        fontSize: 28,
        fontWeight: "800",
        letterSpacing: -0.7,
      },

      subtitle: {
        color: colors.textMuted,
        fontSize: 12,
        marginTop: 3,
      },

      themeButton: {
        alignItems: "center",
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 16,
        borderWidth: 1,
        height: 44,
        justifyContent: "center",
        width: 44,
      },

      themeButtonText: {
        fontSize: 18,
      },
    }
  );
}
