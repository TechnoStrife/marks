const path = require('path')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const BundleTracker = require('webpack-bundle-tracker')
const WriteFilePlugin = require('write-file-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const TerserPlugin = require('terser-webpack-plugin')
const {CleanWebpackPlugin} = require('clean-webpack-plugin')

// const vue_style_loader = process.env.NODE_ENV !== 'production'
//     ? 'vue-style-loader'
//     : MiniCssExtractPlugin.loader;
const vue_style_loader = {
    loader: MiniCssExtractPlugin.loader,
    options: {
        publicPath: ''
    }
}

const css_loader = {
    loader: 'css-loader',
    options: {
        url: true,
    }
}

module.exports = {
    entry: './src/main.js',
    mode: 'development',
    output: {
        path: path.resolve(__dirname, './dist'),
        filename: 'bundle.js',
        publicPath: 'static/'
    },
    plugins: [
        new VueLoaderPlugin(),
        // new BundleTracker({filename: 'webpack-stats.json'}),
        new CleanWebpackPlugin({
            verbose: process.env.NODE_ENV === 'production',
        }),
        new WriteFilePlugin(),
        new MiniCssExtractPlugin({
            filename: 'style.css',
        }),
    ],
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js',
            'static': './static',
            '@': path.resolve(__dirname, './src'),
            'src': path.resolve(__dirname, './src')
        },
        modules: [
            path.resolve(__dirname, 'src'),
            'node_modules'
        ],
        extensions: ['.js', '.vue', '.json', '.scss']
    },
    devServer: {
        historyApiFallback: {
            rewrites: [
                {from: '/', to: '/templates/index.html'},
            ],
            disableDotRule: true
        },
        noInfo: true,
        open: false,
        overlay: true,
        proxy: {
            '/api': 'http://127.0.0.1:8000'
        }
    },
    performance: {
        hints: false
    },
    devtool: 'eval-source-map',
    module: {
        rules: [
            {
                test: /\.js$/,
                use: ["source-map-loader"],
                enforce: "pre"
            },
            {
                test: /\.css$/,
                use: [
                    vue_style_loader,
                    css_loader,
                ]
            },
            {
                test: /\.scss$/,
                use: [
                    vue_style_loader,
                    css_loader,
                    {
                        loader: 'sass-loader',
                        options: {
                            "includePaths": [
                                require('path').resolve(__dirname, 'node_modules')
                            ]
                        }
                    }
                ],
            },
            {
                test: /\.sass$/,
                use: [
                    vue_style_loader,
                    css_loader,
                    'sass-loader?indentedSyntax'
                ],
            },
            {
                test: /\.vue$/,
                loader: 'vue-loader',
                options: {
                    loaders: {
                        'scss': [
                            'vue-style-loader',
                            css_loader,
                            'sass-loader'
                        ],
                        'sass': [
                            'vue-style-loader',
                            css_loader,
                            'sass-loader?indentedSyntax'
                        ],
                        css: [
                            'vue-style-loader',
                            css_loader
                        ]
                    }
                }
            },
            {
                test: /\.(png|jpe?g|gif|ico|webp|svg)(\?.*)?$/,
                use: [
                    // {
                    //     loader: 'file-loader',
                    //     options: {
                    //         name: 'images/[name].[ext]',
                    //     },
                    // },
                    {
                        loader: 'url-loader',
                        options: {
                            limit: 1,
                            name: 'images/[name].[ext]',
                        },
                    },
                ]
            },
            {
                test: /\.(woff2?|ttf)(\?.*)?$/,
                use: [
                    {
                        loader: 'url-loader',
                        options: {
                            limit: 1,
                            name: 'fonts/[name].[ext]',
                        },
                    },
                ]
            },
        ]
    },
}

if (process.env.NODE_ENV === 'production') {
    module.exports.devtool = 'none'
    module.exports.optimization = {
        minimize: true,
        minimizer: [
            new TerserPlugin({
                parallel: true,
                sourceMap: true,
                terserOptions: {
                    output: {
                        comments: false,
                    },
                    compress: {
                        sequences: true,
                        dead_code: true,
                        conditionals: true,
                        booleans: true,
                        unused: true,
                        if_return: true,
                        join_vars: true,
                        drop_console: true
                    },
                    ecma: 6,
                    mangle: true,
                    module: false,
                    toplevel: false,
                    nameCache: null,
                    ie8: false,
                    keep_fnames: true,
                    safari10: false,
                },
            }),
        ]
    }
}
