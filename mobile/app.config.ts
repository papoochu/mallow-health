import {
  ConfigContext,
  ExpoConfig,
} from "expo/config";


export default ({
  config,
}: ConfigContext): ExpoConfig => ({
  ...config,

  name: "Mallow",
  slug: "mallow-health-mobile",

  ios: {
    ...config.ios,
    supportsTablet: true,
    bundleIdentifier: "com.papoochu.mallowhealth",
  },

  android: {
    ...config.android,
    package: "com.papoochu.mallowhealth",
  },

  plugins: [
    ...(config.plugins ?? []),

    [
      "@appeeky/expo-healthkit",
      {
        healthSharePermission:
          "Mallow reads health measurements you choose to share so it can summarize your personal trends, baselines, and relationships.",

        healthUpdatePermission: false,

        isBackgroundDeliveryEnabled: false,
      },
    ],
  ],
});
