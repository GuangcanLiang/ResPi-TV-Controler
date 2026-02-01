package com.tvremote.app

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.util.concurrent.TimeUnit

object RetrofitClient {
    private var retrofit: Retrofit? = null
    private var currentBaseUrl: String = ""

    fun getClient(baseUrl: String): RemoteApiService {
        if (retrofit == null || currentBaseUrl != baseUrl) {
            currentBaseUrl = baseUrl

            // 配置日志拦截器
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }

            // 配置OkHttpClient
            val client = OkHttpClient.Builder()
                .addInterceptor(loggingInterceptor)
                .connectTimeout(5, TimeUnit.SECONDS)
                .readTimeout(5, TimeUnit.SECONDS)
                .writeTimeout(5, TimeUnit.SECONDS)
                .build()

            // 构建Retrofit实例
            retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .addConverterFactory(GsonConverterFactory.create())
                .client(client)
                .build()
        }

        return retrofit!!.create(RemoteApiService::class.java)
    }

    fun resetClient() {
        retrofit = null
        currentBaseUrl = ""
    }
}