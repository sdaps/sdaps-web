import svelte from "rollup-plugin-svelte";
import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import { terser } from "rollup-plugin-terser";
import sveltePreprocess from "svelte-preprocess";
import typescript from "@rollup/plugin-typescript";

const production = !process.env.ROLLUP_WATCH;

export default {
  input: "sdaps_editor/main.ts",
  output: {
    sourcemap: true,
    format: "iife",
    name: "app",
    file: "sdaps_ctl/static/sdaps_ctl/likert_editor.js",
  },
  plugins: [
    svelte({
      // enable run-time checks when not in production
      dev: !production,
      // we'll extract any component CSS out into
      // a separate file - better for performance
      css: (css) => {
        css.write("css/likert_editor.css");
      },
      preprocess: sveltePreprocess(),
    }),
    resolve({
      browser: true,
      dedupe: ["svelte"],
    }),
    commonjs(),
    typescript({
      sourceMap: !production,
      inlineSources: !production,
    }),

    // If we're building for production (yarn build
    // instead of yarn dev), minify
    production && terser(),
  ],
  watch: {
    clearScreen: false,
  },
};
