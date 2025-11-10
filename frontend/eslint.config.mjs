import nextVitals from "eslint-config-next/core-web-vitals";
import globals from "globals";

export default [
  {
    ignores: [".next/**", "node_modules/**", "dist/**", "build/**", "out/**"],
  },
  ...nextVitals,
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",
      "react/no-unescaped-entities": "warn",
      "react-hooks/set-state-in-effect": "warn",
      "react-hooks/exhaustive-deps": "warn",
      "react/no-unknown-property": ["error", { ignore: ["jsx"] }],
    },
  },
];
