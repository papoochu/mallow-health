import React from "react";

import {
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  ThemeColors,
} from "../theme/colors";


export type TabKey =
  | "home"
  | "health"
  | "sleep"
  | "ask";


type BottomNavProps = {
  activeTab: TabKey;
  onSelect: (
    tab: TabKey
  ) => void;
  colors: ThemeColors;
};


const tabs: Array<{
  key: TabKey;
  icon: string;
  label: string;
}> = [
  {
    key: "home",
    icon: "🌿",
    label: "Home",
  },
  {
    key: "health",
    icon: "❤️",
    label: "Health",
  },
  {
    key: "sleep",
    icon: "🌙",
    label: "Sleep",
  },
  {
    key: "ask",
    icon: "💬",
    label: "Ask",
  },
];


export default function BottomNav({
  activeTab,
  onSelect,
  colors,
}: BottomNavProps) {
  const styles = createStyles(
    colors
  );

  return (
    <View
      style={styles.bottomBar}
    >
      {
        tabs.map(
          (
            tab
          ) => {
            const active = (
              activeTab === tab.key
            );

            return (
              <Pressable
                key={tab.key}
                onPress={() => {
                  onSelect(
                    tab.key
                  );
                }}
                style={styles.tab}
              >
                <Text
                  style={[
                    styles.icon,
                    {
                      opacity: (
                        active
                          ? 1
                          : 0.55
                      ),
                    },
                  ]}
                >
                  {tab.icon}
                </Text>

                <Text
                  style={[
                    styles.label,
                    {
                      color: (
                        active
                          ? colors.accent
                          : colors.textMuted
                      ),

                      fontWeight: (
                        active
                          ? "700"
                          : "500"
                      ),
                    },
                  ]}
                >
                  {tab.label}
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

      tab: {
        alignItems: "center",
        flex: 1,
        gap: 2,
        justifyContent: "center",
        paddingVertical: 10,
      },

      icon: {
        fontSize: 19,
      },

      label: {
        fontSize: 11,
      },
    }
  );
}
