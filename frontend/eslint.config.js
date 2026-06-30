import pluginVue from 'eslint-plugin-vue';
import vueTsEslintConfig from '@vue/eslint-config-typescript';
import prettier from '@vue/eslint-config-prettier';

export default [
  { ignores: ['dist/**', 'node_modules/**', 'coverage/**'] },
  ...pluginVue.configs['flat/recommended'],
  ...vueTsEslintConfig(),
  prettier,
  {
    rules: {
      // Single-word panel/view names (Toolbar, App) are intentional here.
      'vue/multi-word-component-names': 'off',
    },
  },
];
