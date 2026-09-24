import React from "react";

import {
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  ViewWindow,
} from "../models/health";

import {
  ThemeColors,
} from "../theme/colors";


type TimeWindowSelectorProps = {
  colors: ThemeColors;
  value: ViewWindow;
  onChange: (
    value: ViewWindow
  ) => void;
};


const OPTIONS: ViewWindow[] = [
  7,
  30,
  90,
];


export default function TimeWindowSelector({
  colors,
  value,
  onChange,
}: TimeWindowSelectorProps) {
  const styles = createStyles(
    colors
  );

  return (
    <View
      style={styles.windowRow}
    >
      {
        OPTIONS.map(
          (
            days
          ) => {
            const selected = (
              value === days
            );

            return (
              <Pressable
                key={days}
                onPress={() => {
                  onChange(
                    days
                  );
                }}
                style={[
                  styles.windowButton,
                  selected
                    ? styles.windowButtonSelected
                    : null,
                ]}
              >
                <Text
                  style={[
                    styles.windowButtonText,
                    selected
                      ? styles.windowButtonTextSelected
                      : null,
                  ]}
                >
                  {days} days
                </Text>
              </Pressable>
            );
          }
        )
      }
    </View>
  );
}


function createStyles(
  colors: ThemeColors,
) {
  return StyleSheet.create(
    {
      windowRow: {
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 18,
        borderWidth: 1,
        flexDirection: "row",
        marginBottom: 22,
        padding: 4,
      },

      windowButton: {
        alignItems: "center",
        borderRadius: 14,
        flex: 1,
        paddingVertical: 10,
      },

      windowButtonSelected: {
        backgroundColor: colors.accentSoft,
      },

      windowButtonText: {
        color: colors.textMuted,
        fontSize: 12,
        fontWeight: "600",
      },

      windowButtonTextSelected: {
        color: colors.accent,
        fontWeight: "800",
      },
    }
  );
}
