import React from "react";

import {
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  HealthSourceMode,
} from "../data/HealthDataContext";

import {
  ThemeColors,
} from "../theme/colors";


type DataSourceCardProps = {
  colors: ThemeColors;
  sourceMode: HealthSourceMode;
  deviceHealthAvailable: boolean;
  connecting: boolean;
  onConnect: () => void;
  onUseDemo: () => void;
};


export default function DataSourceCard({
  colors,
  sourceMode,
  deviceHealthAvailable,
  connecting,
  onConnect,
  onUseDemo,
}: DataSourceCardProps) {
  const styles = createStyles(
    colors
  );

  if (
    sourceMode === "device"
  ) {
    return (
      <View
        style={styles.card}
      >
        <View
          style={styles.copy}
        >
          <Text
            style={styles.title}
          >
            ✓ Device health connected
          </Text>

          <Text
            style={styles.body}
          >
            Mallow is calculating from health data available on this device.
          </Text>
        </View>

        <Pressable
          onPress={onUseDemo}
          style={styles.secondaryButton}
        >
          <Text
            style={styles.secondaryButtonText}
          >
            Demo
          </Text>
        </Pressable>
      </View>
    );
  }


  if (
    !deviceHealthAvailable
  ) {
    return (
      <View
        style={styles.webCard}
      >
        <Text
          style={styles.webTitle}
        >
          Browser preview
        </Text>

        <Text
          style={styles.body}
        >
          This preview uses synthetic demo data. Device health access becomes
          available inside a native development build.
        </Text>
      </View>
    );
  }


  return (
    <View
      style={styles.card}
    >
      <View
        style={styles.copy}
      >
        <Text
          style={styles.title}
        >
          Connect your health data
        </Text>

        <Text
          style={styles.body}
        >
          Read supported measurements from Apple Health or Health Connect.
          Mallow does not write health data.
        </Text>
      </View>

      <Pressable
        disabled={connecting}
        onPress={onConnect}
        style={[
          styles.connectButton,
          connecting
            ? styles.disabled
            : null,
        ]}
      >
        <Text
          style={styles.connectButtonText}
        >
          {
            connecting
              ? "Connecting…"
              : "Connect"
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
      card: {
        alignItems: "center",
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderRadius: 20,
        borderWidth: 1,
        flexDirection: "row",
        marginBottom: 14,
        padding: 14,
      },

      webCard: {
        backgroundColor: colors.surfaceSoft,
        borderColor: colors.border,
        borderRadius: 18,
        borderWidth: 1,
        marginBottom: 14,
        padding: 14,
      },

      copy: {
        flex: 1,
        paddingRight: 12,
      },

      title: {
        color: colors.text,
        fontSize: 13,
        fontWeight: "800",
      },

      webTitle: {
        color: colors.heading,
        fontSize: 12,
        fontWeight: "800",
        marginBottom: 4,
      },

      body: {
        color: colors.textMuted,
        fontSize: 10,
        lineHeight: 15,
        marginTop: 4,
      },

      connectButton: {
        backgroundColor: colors.input,
        borderRadius: 14,
        paddingHorizontal: 14,
        paddingVertical: 10,
      },

      connectButtonText: {
        color: colors.inputText,
        fontSize: 11,
        fontWeight: "800",
      },

      secondaryButton: {
        backgroundColor: colors.accentSoft,
        borderRadius: 14,
        paddingHorizontal: 14,
        paddingVertical: 10,
      },

      secondaryButtonText: {
        color: colors.accent,
        fontSize: 11,
        fontWeight: "800",
      },

      disabled: {
        opacity: 0.6,
      },
    }
  );
}
