import React from "react";

import {
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  ThemeColors,
} from "../theme/colors";


type InsightCardProps = {
  colors: ThemeColors;
  title: string;
  body: string;
  support?: string;
};


export default function InsightCard({
  colors,
  title,
  body,
  support = "Good data support",
}: InsightCardProps) {
  const styles = createStyles(
    colors
  );

  return (
    <View
      style={styles.card}
    >
      <Text
        style={styles.title}
      >
        {title}
      </Text>

      <Text
        style={styles.body}
      >
        {body}
      </Text>

      <View
        style={styles.supportRow}
      >
        <View
          style={styles.dot}
        />

        <Text
          style={styles.supportText}
        >
          {support}
        </Text>
      </View>
    </View>
  );
}


function createStyles(
  colors: ThemeColors,
) {
  return StyleSheet.create(
    {
      card: {
        backgroundColor: colors.pinkSoft,
        borderColor: colors.border,
        borderRadius: 24,
        borderWidth: 1,
        padding: 18,
      },

      title: {
        color: colors.text,
        fontSize: 16,
        fontWeight: "800",
        lineHeight: 22,
      },

      body: {
        color: colors.textMuted,
        fontSize: 12,
        lineHeight: 19,
        marginTop: 9,
      },

      supportRow: {
        alignItems: "center",
        flexDirection: "row",
        marginTop: 13,
      },

      dot: {
        backgroundColor: colors.good,
        borderRadius: 999,
        height: 7,
        marginRight: 7,
        width: 7,
      },

      supportText: {
        color: colors.good,
        fontSize: 10,
        fontWeight: "700",
      },
    }
  );
}
