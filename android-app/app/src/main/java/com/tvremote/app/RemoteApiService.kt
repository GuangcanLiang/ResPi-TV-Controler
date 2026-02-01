package com.tvremote.app

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

// API响应数据类
data class ApiResponse(
    val success: Boolean,
    val message: String? = null,
    val chromium_running: Boolean? = null,
    val server: String? = null
)

// 导航请求
data class NavigateRequest(
    val direction: String
)

// 文本输入请求
data class TextRequest(
    val text: String
)

// URL请求
data class UrlRequest(
    val url: String
)

interface RemoteApiService {
    @POST("api/open")
    fun openBrowser(): Call<ApiResponse>

    @POST("api/close")
    fun closeBrowser(): Call<ApiResponse>

    @POST("api/navigate")
    fun navigate(@Body request: NavigateRequest): Call<ApiResponse>

    @POST("api/text")
    fun inputText(@Body request: TextRequest): Call<ApiResponse>

    @POST("api/url")
    fun openUrl(@Body request: UrlRequest): Call<ApiResponse>

    @POST("api/click")
    fun click(): Call<ApiResponse>

    @GET("api/status")
    fun getStatus(): Call<ApiResponse>
}