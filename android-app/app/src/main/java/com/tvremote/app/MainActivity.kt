package com.tvremote.app

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MainActivity : AppCompatActivity() {

    private lateinit var etServerIp: EditText
    private lateinit var btnConnect: Button
    private lateinit var tvStatus: TextView
    private lateinit var btnOpenBrowser: Button
    private lateinit var btnCloseBrowser: Button
    private lateinit var btnUp: Button
    private lateinit var btnDown: Button
    private lateinit var btnLeft: Button
    private lateinit var btnRight: Button
    private lateinit var btnEnter: Button
    private lateinit var btnBack: Button
    private lateinit var etInputText: EditText
    private lateinit var btnSendText: Button

    private var apiService: RemoteApiService? = null
    private var isConnected = false
    private var serverUrl = ""

    private val handler = Handler(Looper.getMainLooper())
    private var statusCheckRunnable: Runnable? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initViews()
        setupListeners()
    }

    private fun initViews() {
        etServerIp = findViewById(R.id.etServerIp)
        btnConnect = findViewById(R.id.btnConnect)
        tvStatus = findViewById(R.id.tvStatus)
        btnOpenBrowser = findViewById(R.id.btnOpenBrowser)
        btnCloseBrowser = findViewById(R.id.btnCloseBrowser)
        btnUp = findViewById(R.id.btnUp)
        btnDown = findViewById(R.id.btnDown)
        btnLeft = findViewById(R.id.btnLeft)
        btnRight = findViewById(R.id.btnRight)
        btnEnter = findViewById(R.id.btnEnter)
        btnBack = findViewById(R.id.btnBack)
        etInputText = findViewById(R.id.etInputText)
        btnSendText = findViewById(R.id.btnSendText)

        // 禁用控制按钮，直到连接成功
        setControlsEnabled(false)
    }

    private fun setupListeners() {
        // 连接按钮
        btnConnect.setOnClickListener {
            connectToServer()
        }

        // 打开浏览器
        btnOpenBrowser.setOnClickListener {
            apiService?.openBrowser()?.enqueue(createCallback("打开浏览器"))
        }

        // 关闭浏览器
        btnCloseBrowser.setOnClickListener {
            apiService?.closeBrowser()?.enqueue(createCallback("关闭浏览器"))
        }

        // 方向键
        btnUp.setOnClickListener { sendNavigate("up") }
        btnDown.setOnClickListener { sendNavigate("down") }
        btnLeft.setOnClickListener { sendNavigate("left") }
        btnRight.setOnClickListener { sendNavigate("right") }
        btnEnter.setOnClickListener { sendNavigate("enter") }
        btnBack.setOnClickListener { sendNavigate("back") }

        // 发送文本
        btnSendText.setOnClickListener {
            val text = etInputText.text.toString()
            if (text.isNotEmpty()) {
                apiService?.inputText(TextRequest(text))?.enqueue(object : Callback<ApiResponse> {
                    override fun onResponse(call: Call<ApiResponse>, response: Response<ApiResponse>) {
                        if (response.isSuccessful && response.body()?.success == true) {
                            showToast("文本已发送")
                            etInputText.text.clear()
                        } else {
                            showToast("发送失败")
                        }
                    }

                    override fun onFailure(call: Call<ApiResponse>, t: Throwable) {
                        showToast("网络错误: ${t.message}")
                    }
                })
            }
        }
    }

    private fun connectToServer() {
        val ip = etServerIp.text.toString().trim()
        if (ip.isEmpty()) {
            showToast("请输入IP地址")
            return
        }

        serverUrl = "http://$ip:5000/"
        
        // 重置Retrofit客户端以使用新的URL
        RetrofitClient.resetClient()
        apiService = RetrofitClient.getClient(serverUrl)

        // 测试连接
        tvStatus.text = "正在连接..."
        btnConnect.isEnabled = false

        apiService?.getStatus()?.enqueue(object : Callback<ApiResponse> {
            override fun onResponse(call: Call<ApiResponse>, response: Response<ApiResponse>) {
                if (response.isSuccessful && response.body()?.success == true) {
                    isConnected = true
                    tvStatus.text = "已连接到 $ip"
                    tvStatus.setTextColor(getColor(android.R.color.holo_green_light))
                    btnConnect.text = "断开"
                    btnConnect.setOnClickListener { disconnect() }
                    setControlsEnabled(true)
                    startStatusCheck()
                    showToast("连接成功")
                } else {
                    connectionFailed()
                }
                btnConnect.isEnabled = true
            }

            override fun onFailure(call: Call<ApiResponse>, t: Throwable) {
                connectionFailed()
                showToast("连接失败: ${t.message}")
                btnConnect.isEnabled = true
            }
        })
    }

    private fun connectionFailed() {
        isConnected = false
        tvStatus.text = "连接失败"
        tvStatus.setTextColor(getColor(android.R.color.holo_red_light))
        setControlsEnabled(false)
    }

    private fun disconnect() {
        isConnected = false
        stopStatusCheck()
        tvStatus.text = "已断开"
        tvStatus.setTextColor(getColor(android.R.color.darker_gray))
        btnConnect.text = "连接"
        btnConnect.setOnClickListener { connectToServer() }
        setControlsEnabled(false)
        apiService = null
        RetrofitClient.resetClient()
    }

    private fun setControlsEnabled(enabled: Boolean) {
        btnOpenBrowser.isEnabled = enabled
        btnCloseBrowser.isEnabled = enabled
        btnUp.isEnabled = enabled
        btnDown.isEnabled = enabled
        btnLeft.isEnabled = enabled
        btnRight.isEnabled = enabled
        btnEnter.isEnabled = enabled
        btnBack.isEnabled = enabled
        btnSendText.isEnabled = enabled
    }

    private fun sendNavigate(direction: String) {
        apiService?.navigate(NavigateRequest(direction))?.enqueue(createCallback(direction))
    }

    private fun createCallback(action: String): Callback<ApiResponse> {
        return object : Callback<ApiResponse> {
            override fun onResponse(call: Call<ApiResponse>, response: Response<ApiResponse>) {
                if (!response.isSuccessful || response.body()?.success != true) {
                    showToast("$action 失败")
                }
            }

            override fun onFailure(call: Call<ApiResponse>, t: Throwable) {
                showToast("网络错误: ${t.message}")
            }
        }
    }

    private fun startStatusCheck() {
        statusCheckRunnable = object : Runnable {
            override fun run() {
                if (isConnected) {
                    apiService?.getStatus()?.enqueue(object : Callback<ApiResponse> {
                        override fun onResponse(call: Call<ApiResponse>, response: Response<ApiResponse>) {
                            if (!response.isSuccessful || response.body()?.success != true) {
                                // 连接断开
                                handler.post {
                                    disconnect()
                                    showToast("连接已断开")
                                }
                            }
                        }

                        override fun onFailure(call: Call<ApiResponse>, t: Throwable) {
                            handler.post {
                                disconnect()
                                showToast("连接已断开")
                            }
                        }
                    })
                    handler.postDelayed(this, 30000) // 每30秒检查一次
                }
            }
        }
        handler.postDelayed(statusCheckRunnable!!, 30000)
    }

    private fun stopStatusCheck() {
        statusCheckRunnable?.let { handler.removeCallbacks(it) }
    }

    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    override fun onDestroy() {
        super.onDestroy()
        stopStatusCheck()
    }
}