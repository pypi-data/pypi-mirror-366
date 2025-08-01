# PyEdmine

[![](./asset/img/pypi_icon.png)](https://pypi.org/project/edmine/)

[文档] | [数据集信息] | [教育数据挖掘论文列表] | [模型榜单]

[文档]: https://zhijiexiong.github.io/sub-page/pyedmine/document/site/index.html
[数据集信息]: https://zhijiexiong.github.io/sub-page/pyedmine/datasetInfo.html
[教育数据挖掘论文列表]: https://zhijiexiong.github.io/sub-page/pyedmine/paperCollection.html
[模型榜单]: https://zhijiexiong.github.io/sub-page/pyedmine/rankingList.html
[English]: README_EN.md

PyEdmine 是一个面向研究者的，易于开发与复现的**教育数据挖掘**代码库

目前已实现了26个知识追踪模型、7个认知诊断模型、3个习题推荐模型、3个学习路径推荐模型（使用知识追踪模型作为环境模拟器）

我们约定了一个统一、易用的数据文件格式，并已支持 14 个 benchmark dataset

此外，我们设计了一个统一的实验设置，该设置下，知识追踪模型和认知诊断模型可以在习题推荐任务上进行评估


<p align="center">
  <img src="asset/img/ExperimentalFlowChart.jpg" alt="PeEdmine 实验流程图" width="600">
  <br>
  <b>图片</b>: PyEdmine 实验流程图
</p>

各任务的具体实验设置请查阅[此处](https://zhijiexiong.github.io/sub-page/pyedmine/document/site/index.html)

## 安装

### 从pip安装

```bash
pip install edmine
```

### 从源文件安装（推荐）
```bash
git clone git@github.com:ZhijieXiong/pyedmine.git && cd pyedmine
pip install -e .
```

### 主要依赖
必须依赖：pandas、numpy、sklearn、torch

非必需依赖：dgl 是部分认知诊断模型所需的；hyperopt 用于自动化参数调优；wandb 用于记录实验数据；tqdm 用于模型评估阶段。

## 快速开始
请从 GitHub 下载 PyEdmine 的源代码，然后使用 `examples` 目录中提供的脚本完成数据预处理、数据集划分、模型训练与模型评估。PyEdmine 框架的基本流程如下，请按顺序执行：

1、目录配置：通过 `settings.json` 文件配置数据与模型的存放路径，然后运行`set_up.py`以生成必要的目录；

2、数据预处理：下载原始数据集并放置到指定位置，然后使用 `examples` 中提供的脚本进行数据预处理，以获得统一格式的数据文件。数据集信息可在 [这里](https://zhijiexiong.github.io/sub-page/pyedmine/datasetInfo.html) 查看；

3、数据集划分：基于统一格式的数据文件并结合特定实验设置进行数据集划分。PyEdmine 提供了四种实验设置：两种知识追踪任务的设置（分别借鉴 [PYKT](https://dl.acm.org/doi/abs/10.5555/3600270.3601617) 与 [SFKT](https://dl.acm.org/doi/10.1145/3583780.3614988)）、一种认知诊断任务的设置（借鉴 [NCD](https://ojs.aaai.org/index.php/AAAI/article/view/6080)）、一种离线习题推荐任务和一种离线学习路径推荐任务的设置；

4、模型训练：`examples` 中提供了每个模型的训练启动脚本，更多信息可参考 [这里](https://zhijiexiong.github.io/sub-page/pyedmine/document/site/index.html)；

5、模型评估：`examples` 中也提供了每个模型的评估脚本，并根据不同任务实现了不同维度与粒度的评估指标，包括冷启动评估、无偏评估等；

6、其它特性：（1）PyEdmine 针对部分模型实现了基于贝叶斯优化的自动参数调整方法；（2）PyEdmine 可通过参数设置启用 wandb 功能；（3）绘制学生知识状态变化图。

每一步的具体操作说明，请参阅下文。

### 目录配置
在`examples`目录下创建`settings.json`文件，在该文件中配置数据目录和模型目录，格式如下
```json
{
  "FILE_MANAGER_ROOT": "/path/to/save/data",
  "MODELS_DIR": "/path/to/save/model"
}
```
然后运行脚本
```bash
python examples/set_up.py
```
则会自动生成（内置处理代码的）数据集的原始文件存放目录和经过统一处理的文件的存放目录 ，其中各数据集的原始存放目录（位于`/path/to/save/data/dataset_raw`）如下
```
.
├── SLP
│   ├── family.csv
│   ├── psycho.csv
│   ├── school.csv
│   ├── student.csv
│   ├── term-bio.csv
│   ├── term-chi.csv
│   ├── term-eng.csv
│   ├── term-geo.csv
│   ├── term-his.csv
│   ├── term-mat.csv
│   ├── term-phy.csv
│   ├── unit-bio.csv
│   ├── unit-chi.csv
│   ├── unit-eng.csv
│   ├── unit-geo.csv
│   ├── unit-his.csv
│   ├── unit-mat.csv
│   └── unit-phy.csv
├── assist2009
│   └── skill_builder_data.csv
├── assist2009-full
│   └── assistments_2009_2010.csv
├── assist2012
│   └── 2012-2013-data-with-predictions-4-final.csv
├── assist2015
│   └── 2015_100_skill_builders_main_problems.csv
├── assist2017
│   └── anonymized_full_release_competition_dataset.csv
├── edi2020
│   ├── images
│   ├── metadata
│   │   ├── answer_metadata_task_1_2.csv
│   │   ├── answer_metadata_task_3_4.csv
│   │   ├── question_metadata_task_1_2.csv
│   │   ├── question_metadata_task_3_4.csv
│   │   ├── student_metadata_task_1_2.csv
│   │   ├── student_metadata_task_3_4.csv
│   │   └── subject_metadata.csv
│   ├── test_data
│   │   ├── quality_response_remapped_private.csv
│   │   ├── quality_response_remapped_public.csv
│   │   ├── test_private_answers_task_1.csv
│   │   ├── test_private_answers_task_2.csv
│   │   ├── test_private_task_4.csv
│   │   ├── test_private_task_4_more_splits.csv
│   │   ├── test_public_answers_task_1.csv
│   │   ├── test_public_answers_task_2.csv
│   │   └── test_public_task_4_more_splits.csv
│   └── train_data
│       ├── train_task_1_2.csv
│       └── train_task_3_4.csv
├── junyi2015
│   ├── junyi_Exercise_table.csv
│   ├── junyi_ProblemLog_original.csv
│   ├── relationship_annotation_testing.csv
│   └── relationship_annotation_training.csv
├── moocradar
│   ├── problem.json
│   ├── student-problem-coarse.json
│   ├── student-problem-fine.json
│   └── student-problem-middle.json
├── poj
│   └── poj_log.csv
├── slepemapy-anatomy
│   └── answers.csv
├── statics2011
│   └── AllData_student_step_2011F.csv
└── xes3g5m
    ├── kc_level
    │   ├── test.csv
    │   └── train_valid_sequences.csv
    ├── metadata
    │   ├── kc_routes_map.json
    │   └── questions.json
    └── question_level
        ├── test_quelevel.csv
        └── train_valid_sequences_quelevel.csv
```

### 数据预处理
你可以选择使用我们的数据集预处理脚本
```bash
python data_preprocess/kt_data.py
```
该脚本会生成数据集经过统一格式处理后的文件（位于`/path/to/save/data/dataset/dataset_preprocessed`）

注意：`Ednet-kt1`数据集由于原始数据文件数量太多，需要首先使用脚本`examples/data_preprocess/generate_ednet_raw.py`对用户的数据按照5000为单位进行聚合，并且因为该数据集过于庞大，所以预处理默认是只使用交互序列最长5000名用户的数据

或者你可以直接下载已处理好的[数据集文件](https://drive.google.com/drive/folders/1f5hw6PSKWDanVhVVqU1qS-_RxNYNdl9v?usp=sharing)

### 数据集划分
你可以选择使用我们提供的数据集划分脚本，划分好的数据集文件将存放在`/path/to/save/data/dataset/settings/[setting_name]`下
```bash
python examples/knowledge_tracing/prepare_dataset/pykt_setting.py  # 知识追踪
python examples/cognitive_diagnosis/prepare_dataset/ncd_setting.py  # 认知诊断
python examples/exercise_recommendation/preprare_dataset/offline_setting.py  # 习题推荐

```
你也可以直接下载划分后的数据集文件（[pykt_setting](https://www.alipan.com/s/Lek2EDxPfUJ),[sfkt_setting](https://www.alipan.com/s/NfUiLwfoAsK), [ncd_setting](https://drive.google.com/drive/folders/1TDap7nmwPQ7EP4FUpyv6hvo8UkDBeh0R?usp=sharing), [ER_offline_setting](https://www.alipan.com/s/BJQHQn3waA6), [CD4ER_offline_setting](https://drive.google.com/drive/folders/13HHuyOQq31hCP9V8rNUF70ppWvlivxHS?usp=sharing)），然后将其存放在`/path/to/save/data/dataset/settings`目录下

或者你也可以参照我们提供的数据集划分脚本来设计自己的实验处理流程

### 模型训练
对于无需生成包含额外信息的模型，直接运行训练代码即可，如
```bash
python examples/knowledge_tracing/train/dkt.py  # 使用默认参数训练DKT模型
python examples/cognitive_diagnosis/train/ncd.py  # 使用默认参数训练NCD模型
```
对于需要预先生成额外信息的模型，例如DIMKT需要预先计算难度信息、HyperCD需要预先构造知识点超图信息，则需要先运行模型对应的额外信息生成脚本，如
```bash
python examples/knowledge_tracing/dimkt/get_difficulty.py  # 生成DIMKT需要的难度信息
python examples/cognitive_diagnosis/hyper_cd/construct_hyper_graph.py  # 生成HyperCD需要的图信息
```
训练时会得到类似如下的输出
```bash
2025-03-06 02:12:35 epoch 1   , valid performances are main metric: 0.7186   , AUC: 0.7186   , ACC: 0.64765  , MAE: 0.41924  , RMSE: 0.46919  , train loss is predict loss: 0.588902    , current best epoch is 1
2025-03-06 02:12:37 epoch 2   , valid performances are main metric: 0.72457  , AUC: 0.72457  , ACC: 0.63797  , MAE: 0.42329  , RMSE: 0.47456  , train loss is predict loss: 0.556672    , current best epoch is 2
2025-03-06 02:12:39 epoch 3   , valid performances are main metric: 0.72014  , AUC: 0.72014  , ACC: 0.63143  , MAE: 0.43218  , RMSE: 0.47536  , train loss is predict loss: 0.551513    , current best epoch is 2
2025-03-06 02:12:40 epoch 4   , valid performances are main metric: 0.71843  , AUC: 0.71843  , ACC: 0.65182  , MAE: 0.41843  , RMSE: 0.46837  , train loss is predict loss: 0.548907    , current best epoch is 2
2025-03-06 02:12:42 epoch 5   , valid performances are main metric: 0.72453  , AUC: 0.72453  , ACC: 0.65276  , MAE: 0.41841  , RMSE: 0.46684  , train loss is predict loss: 0.547639    , current best epoch is 2
...
2025-03-06 02:13:44 epoch 31  , valid performances are main metric: 0.72589  , AUC: 0.72589  , ACC: 0.65867  , MAE: 0.40794  , RMSE: 0.46316  , train loss is predict loss: 0.532516    , current best epoch is 16
2025-03-06 02:13:47 epoch 32  , valid performances are main metric: 0.72573  , AUC: 0.72573  , ACC: 0.65426  , MAE: 0.41602  , RMSE: 0.46415  , train loss is predict loss: 0.532863    , current best epoch is 16
2025-03-06 02:13:49 epoch 33  , valid performances are main metric: 0.72509  , AUC: 0.72509  , ACC: 0.6179   , MAE: 0.43133  , RMSE: 0.48417  , train loss is predict loss: 0.532187    , current best epoch is 16
2025-03-06 02:13:52 epoch 34  , valid performances are main metric: 0.72809  , AUC: 0.72809  , ACC: 0.63938  , MAE: 0.41994  , RMSE: 0.47377  , train loss is predict loss: 0.533765    , current best epoch is 16
2025-03-06 02:13:54 epoch 35  , valid performances are main metric: 0.72523  , AUC: 0.72523  , ACC: 0.63852  , MAE: 0.42142  , RMSE: 0.47327  , train loss is predict loss: 0.531101    , current best epoch is 16
2025-03-06 02:13:57 epoch 36  , valid performances are main metric: 0.72838  , AUC: 0.72838  , ACC: 0.61986  , MAE: 0.43105  , RMSE: 0.48364  , train loss is predict loss: 0.532342    , current best epoch is 16
best valid epoch: 16  , train performances in best epoch by valid are main metric: 0.74893  , AUC: 0.74893  , ACC: 0.72948  , MAE: 0.34608  , RMSE: 0.42706  , main_metric: 0.74893  , 
valid performances in best epoch by valid are main metric: 0.72902  , AUC: 0.72902  , ACC: 0.59389  , MAE: 0.43936  , RMSE: 0.49301  , main_metric: 0.72902  , 
```
如果训练模型时*use_wandb*参数为True，则可以在[wandb](https://wandb.ai/)上查看模型的损失变化和指标变化

### 模型评估
如果训练模型时*save_model*参数，则会将模型参数文件保存至`/path/to/save/model`目录下，那么可以使用测试集对模型进行评估，如
```bash
python examples/knowledge_tracing/evaluate/sequential_dlkt.py --model_dir_name [model_dir_name] --dataset_name [dataset_name] --test_file_name [test_file_name]
```
其中知识追踪和认知诊断模型除了常规的指标评估外，还可以进行一些细粒度的指标评估，例如冷启动评估，知识追踪的多步预测等，这些评估都可以通过设置对应的参数开启。

以下是不同指标的含义，

#### 知识追踪
- overall 从序列的第2个交互开始预测
- core 论文[Do We Fully Understand Students’ Knowledge States? Identifying and Mitigating Answer Bias in Knowledge Tracing](https://arxiv.org/abs/2308.07779)提出的指标
- user warm start, seqStart25 从序列的第25个交互开始预测
- double warm start, seqStart5QueNum5 从序列的第5个交互开始预测，并且只预测训练中出现次数大于等于5的习题
- user cold start, seqEnd5 只预测序列的前5个交互
- question cold start, queNum5 只预测训练集中出现次数小于等于5的习题
- multi step 论文[pyKT: A Python Library to Benchmark Deep Learning based Knowledge Tracing Models](https://dl.acm.org/doi/abs/10.5555/3600270.3601617)中提到的两种多步预测
- first trans 只预测每个学生交互序列中第一次接触到的知识点
#### 认知诊断
- overall 预测全部测试集
- user cold start, userNum5 只预测训练集中出现次数小于等于5的学生
- question cold start, questionNum5 只预测训练集中出现次数小于等于5的习题
#### 习题推荐
- KG4EX_ACC 论文[KG4Ex: An Explainable Knowledge Graph-Based Approach for Exercise Recommendation](https://dl.acm.org/doi/10.1145/3583780.3614943)中提出的指标，本榜单公布的结果基于DKT计算
- KG4EX_NOV 同KG4EX_ACC
- OFFLINE_ACC 将学生未来练习的习题作为标签，计算准确率
- OFFLINE_NDCG 将学生未来练习的习题作为标签，计算NDCG
- PERSONALIZATION_INDEX 计算给不同学生推荐习题的差异度，作为个性化的指标
#### 学习路径推荐
- AP 
- APR
- RP
- RPR
- NRP
- NRPR

你也可以下载已经[训练好的模型](https://drive.google.com/drive/folders/1KxLgcVDoZwswopCRQEVnBKn4K4gs3lRf?usp=sharing)在我们提供的实验设置上进行模型评估

### 模型自动调参
PyEdmine还支持基于贝叶斯网络的自动调参功能，如
```bash
python examples/cognitive_diagnosis/train/ncd_search_params.py
```
该脚本基于代码中的*parameters_space*变量设置搜参空间

### 绘制学生知识状态变化图
PyEdmine支持使用热力图展示学生知识状态变化过程，对应代码在

```bash
python examples/roster/train/kt_plot.py
```

效果如下图所示

<img src="asset/img/trace_related_cs_change.png" alt="trace_related_cs_change" width="600">
<img src="asset/img/trace_selected_cs_change.png" alt="trace_selected_cs_change" width="600">
<img src="asset/img/trace_single_concept_change.png" alt="trace_single_concept_change" width="600">

## PyEdmine 重要发布
| Releases | Date      |
|----------|-----------|
| v0.1.0   | 3/26/2025 |
| v0.1.1   | 3/31/2025 |
| v0.2.0   | 4/9/2025 |

- `v0.1.0` 初始发布版本
- `v0.1.1` 修复了一些bug，增加了5个知识追踪模型，即ATDKT、CLKT、DTransformer、GRKT、HDLPKT
- `v0.2.0` beta版本，但是GRKT模型训练会报错（NaN），尚未解决

## 数据集扩展
[edi2020-task-34-question.json](./edi2020-task34-question.json)是在 **EDi2020 Task 3&4** 提供的数学题目图像数据基础上，进行的非正式扩展版本。原始数据集中仅包含题目图像，未提供对应的文本信息。为增强其在知识追踪与文本建模任务中的适用性，我补充提取了题目的文本内容，并参考了 [Kaggle Eedi: Mining Misconceptions in Mathematics](https://www.kaggle.com/competitions/eedi-mining-misconceptions-in-mathematics) 的数据格式进行组织，以便于后续使用。

文本提取流程相对简化，主要包括：

使用 OCR 工具识别图像中的文字；

对于 OCR 无法有效识别的题目，使用多模态大模型生成文本描述；

结合人工进行了简单核对与修正。

尽管整体文本信息具有较高准确性，但仍可能存在个别提取错误。这是一个**非官方的扩展版本**，欢迎社区参考与使用，但建议在具体研究中结合自身需求进行验证与清洗。

## 开发中

### 学习路径规划任务

## 参考代码库

- [PYKT](https://github.com/pykt-team/pykt-toolkit)
- [EduDATA](https://github.com/bigdata-ustc/EduData)
- [EduKTM](https://github.com/bigdata-ustc/EduKTM)
- [EduCDM](https://github.com/bigdata-ustc/EduCDM)
- [RecBole](https://github.com/RUCAIBox/RecBole)
- [其它论文代码仓库](https://zhijiexiong.github.io/sub-page/pyedmine/paperCollection.html)

## 贡献

如果您遇到错误或有任何建议，请通过 [Issue](https://github.com/ZhijieXiong/pyedmine/issuesWe) 进行反馈

我们欢迎任何形式的贡献，包括推荐论文将其添加到[论文列表](https://zhijiexiong.github.io/sub-page/pyedmine/paperCollection.html)中、修复 bug、添加新特性、或提供已训练的模型权重。

如果您希望推荐论文，请在[Discussion](https://github.com/ZhijieXiong/pyedmine/discussions/7)中进行推荐。

如果您希望贡献代码，且没有合并冲突，可以直接提交 Pull Request；若存在潜在冲突或重大更改，请先通过 issue 描述问题，再提交 Pull Request。

如果您希望提供已训练模型的权重，请发送邮件至 18800118477@163.com，并附上模型权重和训练脚本，或包含这些内容的可访问链接。

若您提供的是 PyEdmine 尚未实现的模型，请先通过 Pull Request 贡献模型实现代码，再通过邮件联系。

## 免责声明
PyEdmine 基于 [MIT License](./LICENSE) 进行开发，本项目的所有数据和代码只能被用于学术目的
