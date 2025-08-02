from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                           QSpinBox, QPushButton, QWidget, QLabel, QHBoxLayout,
                           QDialogButtonBox, QGridLayout, QComboBox, QListView, QListWidget, QListWidgetItem, QAbstractItemView,
                           QProgressDialog, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont
from shiyunzi.utils.models import StableDiffusion

# 假设有一个获取模型列表的工具函数
from shiyunzi.utils.stable_diffusion_util import (
    get_sd_models, get_sd_loras, get_sd_samplers, get_sd_schedulers
)

class LoadingDialog(QProgressDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle("加载中")
        self.setLabelText(title)
        self.setCancelButton(None)
        self.setRange(0, 0)  # 设置为循环进度条
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumWidth(300)  # 设置最小宽度
        self.setMinimumHeight(100)  # 设置最小高度
        self.setStyleSheet("""
            QProgressDialog {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                min-width: 300px;
                min-height: 100px;
            }
            QLabel {
                color: #1e293b;
                font-size: 14px;
                border: none;
                font-family: "Microsoft YaHei UI";
                padding: 16px;
            }
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                text-align: center;
                background-color: #f8fafc;
                min-height: 8px;
                max-height: 8px;
            }
            QProgressBar::chunk {
                background-color: #6366f1;
                border-radius: 3px;
            }
        """)

class SDEditDialog(QDialog):
    def __init__(self, sd_data=None, parent=None):
        super().__init__(parent)
        self.sd_data = sd_data
        self.setup_ui()
        # 初始化时加载所有数据
        self.load_all_data()
        
    def load_all_data(self):
        """加载所有需要的数据"""
        loading = LoadingDialog("正在加载数据...", self)
        loading.show()
        
        # 加载模型列表
        models = get_sd_models()
        self.model.clear()
        if models:
            self.model.addItems(models)
            if self.sd_data and self.sd_data.model:
                index = self.model.findText(self.sd_data.model)
                if index >= 0:
                    self.model.setCurrentIndex(index)
        else:
            self.model.addItem("无可用模型")
            
        # 加载LoRA列表
        loras = get_sd_loras()
        self.lora.clear()
        if loras:
            for lora_name in loras:
                item = QListWidgetItem(lora_name)
                self.lora.addItem(item)
                # 如果是编辑模式，检查是否需要选中
                if self.sd_data and self.sd_data.lora:
                    try:
                        import json
                        lora_selected = json.loads(self.sd_data.lora)
                        if isinstance(lora_selected, list) and lora_name in lora_selected:
                            item.setSelected(True)
                    except Exception:
                        pass
        else:
            self.lora.addItem("无可用LoRA")
            
        # 加载采样器列表
        samplers = get_sd_samplers()
        self.sampler.clear()
        if samplers:
            self.sampler.addItems(samplers)
            if self.sd_data and self.sd_data.sampler:
                index = self.sampler.findText(self.sd_data.sampler)
                if index >= 0:
                    self.sampler.setCurrentIndex(index)
        else:
            self.sampler.addItem("无可用采样器")
            
        # 加载调度器列表
        schedulers = get_sd_schedulers()
        self.scheduler.clear()
        if schedulers:
            self.scheduler.addItems(schedulers)
            if self.sd_data and self.sd_data.scheduler:
                index = self.scheduler.findText(self.sd_data.scheduler)
                if index >= 0:
                    self.scheduler.setCurrentIndex(index)
        else:
            self.scheduler.addItem("无可用调度器")
            
        loading.close()
        
    def setup_ui(self):
        self.setWindowTitle("编辑 Stable Diffusion 配置")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题
        title_container = QWidget()
        title_container.setStyleSheet("background-color: #ffffff;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(32, 32, 32, 32)
        
        title = QLabel("编辑 Stable Diffusion 配置" if self.sd_data else "添加 Stable Diffusion 配置")
        title.setFont(QFont("Microsoft YaHei UI", 20, QFont.Weight.DemiBold))
        title.setStyleSheet("color: #1e293b; border: none;")
        title_layout.addWidget(title)
        
        layout.addWidget(title_container)
        
        # 表单容器
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
            }
        """)
        
        # 使用网格布局替代表单布局
        grid_layout = QGridLayout(form_container)
        grid_layout.setContentsMargins(32, 32, 32, 32)
        grid_layout.setHorizontalSpacing(24)  # 减小水平间距
        grid_layout.setVerticalSpacing(16)    # 减小垂直间距
        
        # 创建输入字段
        self.name = QLineEdit()
        
        # 模型选择下拉框
        self.model = QComboBox()
        self.model.setEditable(False)
        self.model.setMinimumWidth(200)
        self.model.setFixedHeight(40)  # 设置固定高度
        self.model.setView(QListView())
        self.model.view().setStyleSheet("""
            QListView {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
                color: #1e293b;
                padding: 4px 0;
                selection-background-color: #6366f1;
                selection-color: #ffffff;
                outline: none;
            }
            QListView::item {
                padding: 8px 16px;
                border: none;
                min-height: 24px;  # 设置项目最小高度
            }
            QListView::item:selected {
                background: #6366f1;
                color: #ffffff;
            }
            QListView::item:hover {
                background: #e2e8f0;
                color: #1e293b;
            }
        """)

        # LoRA多选下拉
        self.lora = QListWidget()
        self.lora.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.lora.setMinimumHeight(240)  # 增加高度为原来的两倍
        self.lora.setMaximumHeight(240)  # 增加高度为原来的两倍
        self.lora.setStyleSheet("""
            QListWidget {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background: white;
                font-size: 13px;
                min-height: 24px;
            }
            QListWidget::item {
                padding: 8px 16px;
            }
            QListWidget::item:selected {
                background: #6366f1;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background: #e2e8f0;
                color: #1e293b;
            }
        """)

        self.steps = QSpinBox()
        self.cfg = QDoubleSpinBox()
        
        # 调度器下拉框
        self.scheduler = QComboBox()
        self.scheduler.setEditable(False)
        self.scheduler.setMinimumWidth(200)
        self.scheduler.setView(QListView())
        self.scheduler.view().setStyleSheet(self.model.view().styleSheet())
        
        # 采样器下拉框
        self.sampler = QComboBox()
        self.sampler.setEditable(False)
        self.sampler.setMinimumWidth(200)
        self.sampler.setView(QListView())
        self.sampler.view().setStyleSheet(self.model.view().styleSheet())
        
        self.seed = QSpinBox()
        self.width = QSpinBox()
        self.height = QSpinBox()
        
        # 设置默认值和范围
        self.steps.setRange(1, 150)
        self.steps.setValue(20)
        
        self.cfg.setRange(1.0, 30.0)
        self.cfg.setSingleStep(0.5)
        self.cfg.setValue(7.0)
        self.cfg.setDecimals(1)  # 设置小数点位数为1
        
        self.seed.setRange(-1, 999999999)
        self.seed.setValue(-1)
        
        self.width.setRange(64, 2048)
        self.width.setValue(512)
        
        self.height.setRange(64, 2048)
        self.height.setValue(512)
        
        # 如果是编辑模式，填充现有数据
        if self.sd_data:
            self.name.setText(self.sd_data.name)
            self.steps.setValue(self.sd_data.steps)
            self.cfg.setValue(self.sd_data.cfg)
            self.seed.setValue(self.sd_data.seed)
            self.width.setValue(self.sd_data.width)
            self.height.setValue(self.sd_data.height)
        
        # 设置样式
        input_style = """
            QLineEdit, QSpinBox, QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #6366f1;
            }
            QComboBox {
                padding-right: 24px;
                background: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
            }
            QSpinBox::up-button {
                border-top-right-radius: 6px;
                border-left: none;
                border-bottom: none;
            }
            QSpinBox::down-button {
                border-bottom-right-radius: 6px;
                border-left: none;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #e2e8f0;
            }
            QSpinBox::up-arrow {
                image: url(up_arrow.png);
                width: 8px;
                height: 8px;
            }
            QSpinBox::down-arrow {
                image: url(down_arrow.png);
                width: 8px;
                height: 8px;
            }
            QLabel {
                font-size: 13px;
                color: #475569;
                border: none;
                padding: 0 8px;
            }
        """
        
        # 为所有控件设置统一样式
        for widget in [self.name, self.model,
                      self.steps, self.cfg,
                      self.scheduler, self.sampler, self.seed,
                      self.width, self.height]:
            widget.setStyleSheet(input_style)

        # 添加表单字段到网格布局
        def add_field(label_text, widget, row, col, row_span=1):
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #475569;
                    border: none;
                    padding: 0 8px;
                }
            """)
            grid_layout.addWidget(label, row, col * 2)
            grid_layout.addWidget(widget, row, col * 2 + 1, row_span, 1)  # 添加row_span参数
            
            # 设置列宽比例
            if col == 0:
                grid_layout.setColumnStretch(col * 2, 1)     # 标签列
                grid_layout.setColumnStretch(col * 2 + 1, 2) # 控件列
            
        # 左列
        add_field("名称:", self.name, 0, 0)
        add_field("模型:", self.model, 1, 0)
        add_field("LoRA:", self.lora, 2, 0, 3)  # 让LoRA跨越3行
        add_field("步数:", self.steps, 5, 0)
        
        # 右列
        add_field("CFG:", self.cfg, 0, 1)
        add_field("调度器:", self.scheduler, 1, 1)
        add_field("采样器:", self.sampler, 2, 1)
        add_field("宽度:", self.width, 3, 1)
        add_field("高度:", self.height, 4, 1)
        add_field("种子:", self.seed, 5, 1)
        
        layout.addWidget(form_container)
        
        # 按钮容器
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #ffffff;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(32, 32, 32, 32)
        button_layout.setSpacing(16)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setFont(QFont("Microsoft YaHei UI", 13))
        cancel_btn.setMinimumSize(0, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
            QPushButton:pressed {
                background-color: #cbd5e1;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.setFont(QFont("Microsoft YaHei UI", 13))
        save_btn.setMinimumSize(0, 40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #4338ca;
            }
        """)
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)
        
        layout.addWidget(button_container)
        
    def save_config(self):
        # 获取多选的lora
        import json
        lora_selected = [item.text() for item in self.lora.selectedItems() if item.text() != "无可用LoRA"]
        lora_str = json.dumps(lora_selected, ensure_ascii=False)
        
        if self.sd_data:
            # 更新现有配置
            self.sd_data.name = self.name.text()
            self.sd_data.model = self.model.currentText()
            self.sd_data.lora = lora_str
            self.sd_data.steps = self.steps.value()
            self.sd_data.cfg = self.cfg.value()
            self.sd_data.scheduler = self.scheduler.currentText()
            self.sd_data.sampler = self.sampler.currentText()
            self.sd_data.seed = self.seed.value()
            self.sd_data.width = self.width.value()
            self.sd_data.height = self.height.value()
            self.sd_data.save()
        else:
            # 创建新配置
            StableDiffusion.create(
                name=self.name.text(),
                model=self.model.currentText(),
                lora=lora_str,
                steps=self.steps.value(),
                cfg=self.cfg.value(),
                scheduler=self.scheduler.currentText(),
                sampler=self.sampler.currentText(),
                seed=self.seed.value(),
                width=self.width.value(),
                height=self.height.value()
            )
        
        self.accept()