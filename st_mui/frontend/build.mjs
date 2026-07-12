/**
 * Build script that produces a separate Vite library build for each component.
 * Each component gets its own index-[hash].js in its own build/ directory.
 */
import { build } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";
import process from "node:process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// Production is the default so a plain `npm run build` (what CI runs when
// packaging the wheel) minifies and skips sourcemaps. Development builds opt in
// via `npm run build:dev` / `npm run dev`, which set NODE_ENV=development.
const isProd = process.env.NODE_ENV !== "development";
const isWatch = process.argv.includes("--watch");

const components = [
  { name: "date_picker", entry: "./src/date_picker/index.tsx" },
  { name: "time_picker", entry: "./src/time_picker/index.tsx" },
  { name: "date_time_picker", entry: "./src/date_time_picker/index.tsx" },
  { name: "date_range_picker", entry: "./src/date_range_picker/index.tsx" },
  { name: "date_time_range_picker", entry: "./src/date_time_range_picker/index.tsx" },
  { name: "tree_view", entry: "./src/tree_view/index.tsx" },
];

async function buildComponent(component) {
  const outDir = path.resolve(__dirname, `../${component.name}/frontend/build`);
  console.log(`Building ${component.name} -> ${outDir}`);

  await build({
    root: __dirname,
    base: "./",
    plugins: [react()],
    define: {
      "process.env.NODE_ENV": JSON.stringify(
        process.env.NODE_ENV || "production"
      ),
    },
    build: {
      // Vite 8 minifies with oxc (Rolldown); the old "esbuild" value now
      // requires esbuild as a separate install and is deprecated.
      minify: isProd,
      outDir,
      emptyOutDir: true,
      sourcemap: !isProd,
      watch: isWatch ? {} : null,
      lib: {
        entry: component.entry,
        name: component.name,
        formats: ["es"],
        fileName: "index-[hash]",
      },
    },
    logLevel: "info",
  });
}

async function main() {
  for (const component of components) {
    await buildComponent(component);
  }
  console.log("\nAll components built successfully!");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
