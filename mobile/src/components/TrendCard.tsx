import React from "react";

import {
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  ThemeColors,
} from "../theme/colors";


type TrendCardProps = {
  colors: ThemeColors;
  title: string;
  value: string;
  caption: string;
  trendLabel: string;
  data: number[];
};


export default function TrendCard({
  colors,
  title,
  value,
  caption,
  trendLabel,
  data,
}: TrendCardProps) {
  const styles = createStyles(
    colors
  );

  const finiteValues = data.filter(
    (
      item
    ) => Number.isFinite(
      item
    )
  );

  const minimum = (
    finiteValues.length > 0
      ? Math.min(
          ...finiteValues
        )
      : 0
  );

  const maximum = (
    finiteValues.length > 0
      ? Math.max(
          ...finiteValues
        )
      : 1
  );

  const range = Math.max(
    maximum - minimum,
    0.001,
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

      <View
        style={styles.summaryRow}
      >
        <View>
          <Text
            style={styles.value}
          >
            {value}
          </Text>

          <Text
            style={styles.caption}
          >
            {caption}
          </Text>
        </View>

        <View
          style={styles.badge}
        >
          <Text
            style={styles.badgeText}
          >
            {trendLabel}
          </Text>
        </View>
      </View>

      <View
        style={styles.sparkline}
      >
        {
          data.map(
            (
              item,
              index,
            ) => {
              const normalized = (
                item - minimum
              ) / range;

              const height = (
                18
                + normalized * 74
              );

              return (
                <View
                  key={
                    `${index}-${item}`
                  }
                  style={styles.sparkColumn}
                >
                  <View
                    style={[
                      styles.sparkBar,
                      {
                        height,
                        opacity: (
                          0.45
                          + index
                          / Math.max(
                            data.length,
                            1
                          )
                          / 1.8
                        ),
                      },
                    ]}
                  />
                </View>
              );
            }
          )
        }
      </View>

      <View
        style={styles.footer}
      >
        <Text
          style={styles.footerText}
        >
          Earlier
        </Text>

        <Text
          style={styles.footerText}
        >
          Recent
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
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 24,
        borderWidth: 1,
        padding: 18,
      },

      title: {
        color: colors.heading,
        fontSize: 15,
        fontWeight: "800",
        marginBottom: 12,
      },

      summaryRow: {
        alignItems: "flex-start",
        flexDirection: "row",
        justifyContent: "space-between",
      },

      value: {
        color: colors.text,
        fontSize: 26,
        fontWeight: "800",
      },

      caption: {
        color: colors.textMuted,
        fontSize: 10,
        marginTop: 2,
      },

      badge: {
        backgroundColor: colors.goodSoft,
        borderRadius: 999,
        maxWidth: "55%",
        paddingHorizontal: 10,
        paddingVertical: 7,
      },

      badgeText: {
        color: colors.good,
        fontSize: 10,
        fontWeight: "700",
        textAlign: "center",
      },

      sparkline: {
        alignItems: "flex-end",
        flexDirection: "row",
        gap: 6,
        height: 110,
        marginTop: 20,
      },

      sparkColumn: {
        flex: 1,
        height: "100%",
        justifyContent: "flex-end",
      },

      sparkBar: {
        backgroundColor: colors.chartLine,
        borderRadius: 999,
        minHeight: 8,
        width: "100%",
      },

      footer: {
        flexDirection: "row",
        justifyContent: "space-between",
        marginTop: 8,
      },

      footerText: {
        color: colors.textMuted,
        fontSize: 9,
      },
    }
  );
}
