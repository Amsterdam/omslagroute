var path = require("path")
var webpack = require('webpack')

const { VueLoaderPlugin } = require('vue-loader')

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';

  // Define feature flags based on environment
  const definePluginArgs = {
    __VUE_OPTIONS_API__: JSON.stringify(true),
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(true),
    __VUE_PROD_DEVTOOLS__: JSON.stringify(false)
  };

  return {
    context: __dirname,
    mode: isProduction ? 'production' : 'development',
    devtool: 'cheap-module-source-map', 
    entry: {
      'case-status': './assets/js/case-status',
      'case': './assets/js/case',
    }, // entry point of our app. assets/js/index.js should require other js modules and dependencies it needs

    output: {
        path: path.resolve('./assets/bundles/'),
        filename: "[name].js",
    },

    module: {
      rules: [
        {
          test: /\.vue$/,
          loader: 'vue-loader'
        },
        {
          test: /\.(scss|css)$/,
          use: [
              "style-loader",
              "css-loader",
              "sass-loader"
          ]
        },
        {
          test: /\.js$/,
          exclude: /node_modules/,
          loader: 'babel-loader'
        },
      ]
    },
    resolve: {
      alias: {
        'vue$': isProduction ? 'vue/dist/vue.runtime.esm-bundler.js' : 'vue/dist/vue.esm-bundler.js',
      },
      extensions: [".*", ".js", ".vue", ".json"]
    },
    plugins: [
      new VueLoaderPlugin(),
      // Define feature flags as global constants
      new webpack.DefinePlugin(definePluginArgs)
    ],
  }
}