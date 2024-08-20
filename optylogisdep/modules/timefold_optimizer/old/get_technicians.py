from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader


dataloader = DataLoader()
pers_gr = dataloader.pers_gr
pers_st = dataloader.pers_st



if __name__ == '__main__':
    print(pers_gr)
    print(pers_st)
