import os, sys, argparse

# from distutils.util import strtobool  # 字符串转布尔值的工具（已弃用）
# 替换原代码中的导入
from setuptools._distutils.util import strtobool  # Python 3.10+

from pprint import pprint             # 美观打印
import libs.FULL.src.v8.trainer as trainer  # 训练模块
import libs.FULL.src.v8.tester as tester    # 测试模块

set_modes    = {'train','test'}   
set_devices  = {'cuda','cpu'}
set_datasets = {'lolv1', 'lolv2', 'lolsyn', 'lolve', 'adobe5k', 'misc'}

def get_args():

    # 参数分类：
    # - 基础设置（模式/设备/GPU等）
    # - 路径配置（数据集/模型/结果路径）
    # - 功能开关（恢复训练/保存结果等）
    # - 优化参数（学习率/batch大小等）
    # - 损失函数权重（wc/ws/we等）

    config = argparse.ArgumentParser(description='RRR Fusion main function.')
    # Setup
    config.add_argument('--mode', type=str, default='test', choices=set_modes, help='mode type: '+str(set_modes))
    config.add_argument('--gpuId', type=str, default="0", help='ID of the GPU device to be used')
    config.add_argument('--device', type=str, default='cuda', choices=set_devices, help='device type: '+str(set_devices))
    config.add_argument('--num_workers', type=int, default=2, help='number of parallel workers for data loading') # 2,10
    config.add_argument('--resume', default=False, type=lambda x: bool(strtobool(str(x.strip()))), help='resume training. picks model weights from p_model')

    # Paths
    config.add_argument('--dataset', type=str, default='lolv1', choices=set_datasets, help='dataset name:'+str(set_datasets))
    config.add_argument('--p_trainDir', type=str, default='D:/course/LLE/dataset/LOLdataset/our485/low', help='dataset folder path for input images')
    config.add_argument('--p_trainList', type=str, default='D:/course/LLE/dataset/LOLdataset/our485/trainList.txt', help='path for list of inputs')
    config.add_argument('--p_trainGtDir', type=str, default='D:/course/LLE/dataset/LOLdataset/our485/high', help='gt folder path')

    config.add_argument('--p_valDir', type=str, default=None, help='dataset folder path for input images')
    config.add_argument('--p_valList', type=str, default=None, help='path for list of inputs')
    config.add_argument('--p_valGtDir', type=str, default=None, help='gt folder path')

    config.add_argument('--p_testDir', type=str, default="D:/course/LLE/dataset/LOLdataset/eval15/low", help='dataset folder path for input images')
    config.add_argument('--p_testList', type=str, default="D:/course/LLE/dataset/LOLdataset/eval15/testList.txt", help='path for list of inputs')
    config.add_argument('--p_testGtDir', type=str, default="D:/course/LLE/dataset/LOLdataset/eval15/high", help='gt folder path')

    config.add_argument('--p_model', type=str, default='D:/course/LLE/dataset/LOLdataset/resDir/2025_04_09_15_04_59/RRNet_lolv1_48.pt', help='saved model path for testing.')
    config.add_argument('--p_resDir', type=str, default='D:/course/LLE/dataset/LOLdataset/resDir', help='where to save results')

    # Flags
    config.add_argument('--f_valFromTrain', type=lambda x: bool(strtobool(str(x.strip()))), default=False, help='Use validation set or not. If p_valDir is None take 10 percent of training as valset.')
    config.add_argument('--f_OverExp', type=lambda x: bool(strtobool(str(x.strip()))), default=False, help='Over Exposed image ?')
    config.add_argument('--f_saveRes', type=lambda x: bool(strtobool(str(x.strip()))), default=True, help='Save enhanced results ?')
    config.add_argument('--f_RGB', type=lambda x: bool(strtobool(str(x.strip()))), default=True, help='Save enhanced results ?')
    config.add_argument('--f_eval', type=lambda x: bool(strtobool(str(x.strip()))), default=True, help='Save enhanced results ?')
    config.add_argument('--f_denoise', type=lambda x: bool(strtobool(str(x.strip()))), default=True, help='Save enhanced results ?')
    # Optim params
    config.add_argument('--lr', type=float, default=0.01, help='initial learning rate')  
    config.add_argument('--imsize', type=int, default=512, help='size to which images will be resized')
    config.add_argument('--epochs', type=int, default=50, help='number of epochs')
    config.add_argument('--lr_step', type=int, default=1)
    config.add_argument('--lr_decay', type=float, default=1.0)
    config.add_argument('--batch_size', type=int, default=1, help='batch size')
    config.add_argument('--maxIt', type=int, default=3) # max iterations
    config.add_argument('--factors', type=int, default=5)
    config.add_argument('--dataMean', type=float, default=0.05)
    config.add_argument('--seed', type=int, default=2)
    config.add_argument('--extn', type=str, default='.png')
    # Loss params
    config.add_argument('--freeze', type=int, default=25)
    config.add_argument('--etaA', type=float, default=0.1)
    config.add_argument('--wc', type=float, default=10)   
    config.add_argument('--ws', type=float, default=0)
    config.add_argument('--we', type=float, default=2)
    config.add_argument('--wt', type=float, default=2)
    config.add_argument('--wf', type=float, default=2)
    config.add_argument('--wd', type=float, default=0)
    
    return config.parse_args()


def chk_args(config):

    # 检查模式/设备/数据集是否合法
    # 验证文件路径是否存在
    # 检查数值参数范围（学习率>0，epochs>0等）

    config.mode     = config.mode.lower()
    if config.mode not in set_modes: sys.exit('ERROR: Incorrect mode (should be : '+str(set_modes))
    config.device   = config.device.lower()
    if config.device not in set_devices: sys.exit('ERROR: Incorrect device type (should be :'+str(set_devices))
    config.dataset  = config.dataset.lower()
    if config.dataset not in set_datasets: sys.exit('ERROR: Dataset not found (should be :'+str(set_datasets))
    if config.resume:
        if not (os.path.exists(config.p_model)): sys.exit('ERROR: Model_path incorrect.')
    if config.mode=='train':
        if not (os.path.exists(config.p_trainDir)): sys.exit('ERROR: Dataset_path incorrect.')
        if not (os.path.exists(config.p_trainList)): sys.exit('ERROR: Train_inList_path incorrect.')
        if not (os.path.exists(config.p_trainGtDir)): sys.exit('ERROR: Train_gt_path incorrect.')
    if config.mode=='test':
        if not (os.path.exists(config.p_model)): sys.exit('ERROR: Model_path incorrect.')
        if not (os.path.exists(config.p_testDir)): sys.exit('ERROR: TestDir path incorrect.')
        if (not (config.p_testList==None)) and (not os.path.exists(config.p_testList)): sys.exit('ERROR: Train_inList_path incorrect.')
        if (not (config.p_testGtDir==None)) and (not os.path.exists(config.p_testGtDir)): sys.exit('ERROR: Test_gt_path incorrect.')
    if not config.p_resDir==None:   os.makedirs(config.p_resDir, exist_ok=True)
    if not (config.lr>0 and isinstance(config.lr, float)): sys.exit('ERROR: Incorrect learning rate value.')
    if not (config.epochs>0) and isinstance(config.epochs, int): sys.exit('ERROR: Incorrect pre_training epochs value.')
    if not (config.lr_step>0 and isinstance(config.lr_step, int)): sys.exit('ERROR: Incorrect learning step value.')
    if not (config.lr_decay>0 and isinstance(config.lr_decay, float)): sys.exit('ERROR: Incorrect learning decay value.')
    if not (config.batch_size>0 and isinstance(config.batch_size, int)): sys.exit('ERROR: Incorrect batch_size value.')
         
    return config


def main():
    config = get_args()
    config = chk_args(config)
    os.environ["CUDA_LAUNCH_BLOCKING"] = "False"
    os.environ["CUDA_VISIBLE_DEVICES"] = config.gpuId
    if config.mode == 'train':
        pprint(vars(config))
        trainer.train(config)
    elif config.mode == 'test':
        tester.test(config)


if __name__=='__main__':
    main()
else:
    print(f"建立了一个worker进程（模块名: {__name__}）")