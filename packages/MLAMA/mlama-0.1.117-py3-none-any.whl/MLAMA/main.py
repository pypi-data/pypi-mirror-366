#Wave class to represent each waves

class Wave:
  """
  A class to represent a wave.
  Attributes:
    waveID (int): Unique ID for each wave
    startDate (Date object): Start date of the wave
    endDate (Date object): End date of the wave
    trainStartDate (Date object): Start date of the training data
    trainEndDate (Date object): End date of the training data
    testStartDate (Date object): Start date of the testing data
    testEndDate (Date object): End date of the testing data
    df (DataFrame): Dataframe of the wave
  Methods:
    print_wave: Prints the wave information
    get_wave_dates_with_delay: Gets the wave data, train data, and test data with delay
    get_wave_test_start_date_with_delay: Gets the test start date with delay
    get_wave_df: Gets the wave data as a dataframe
  """
  def __init__(self, waveID, startDate, endDate,
               trainStartDate, trainEndDate, testStartDate, testEndDate, df):
    """
    Constructs all the necessary attributes for the wave object.
    Args:
      waveID (int): Unique ID for each wave
      startDate (Date object): Start date of the wave
      endDate (Date object): End date of the wave
      trainStartDate (Date object): Start date of the training data
      trainEndDate (Date object): End date of the training data
      testStartDate (Date object): Start date of the testing data
      testEndDate (Date object): End date of the testing data
      df (DataFrame): Dataframe of the wave
    """
    self.waveID = waveID
    self.startDate = startDate
    self.endDate = endDate

    self.trainStartDate = trainStartDate
    self.trainEndDate = trainEndDate
    self.testStartDate = testStartDate
    self.testEndDate = testEndDate
    self.df = df.loc[self.startDate:self.endDate]

  def print_wave(self):
    print('Wave', self.waveID, ':')
    print('All:', self.startDate, ':', self.endDate)
    print('Train:', self.trainStartDate, ':', self.trainEndDate)
    print('Test:', self.testStartDate, ':', self.testEndDate)

  

  def get_wave_dates_with_delay_JMM(self, delay):#JMM definition. 
    """
    Gets the wave data, train data, and test data after calculating delay.
    Wave start remains the same, wave end delayed.
    Train start remains the same, train end not delayed. (Only change then Yushu definition)
    Test start and end delayed.
    Args:
      wave:Wave object
      delay (int): Delay in weeks
    Returns:
      wave_data (DataFrame): Wave data with delay
      train_data (DataFrame): Train data with delay
      test_data (DataFrame): Test data with delay
    """
    ############WAVE data
    start = datetime.datetime.strptime(self.startDate,"%Y-%m-%d")#start fixed, irrespective of delay
    start_str = start.strftime("%Y-%m-%d")

    e = datetime.datetime.strptime(self.endDate,"%Y-%m-%d")
    w = datetime.timedelta(weeks=delay)
    end = e + w#end delayed
    end_str = end.strftime("%Y-%m-%d")
    #print('Wave:', start_str, ':', end_str)
    wave_data = df.loc[start_str:end_str]

    ############Train data
    start = datetime.datetime.strptime(self.trainStartDate,"%Y-%m-%d")#train start fixed, irrespective of delay
    start_str = start.strftime("%Y-%m-%d")

    e = datetime.datetime.strptime(self.trainEndDate,"%Y-%m-%d")
    #w = datetime.timedelta(weeks=delay)
    end = e #end not delayed
    end_str = end.strftime("%Y-%m-%d")
    #print('Train:', start_str, ':', end_str)
    train_data = df.loc[start_str:end_str]

    ############Test data
    s = datetime.datetime.strptime(self.testStartDate,"%Y-%m-%d")#test start date delayed
    w = datetime.timedelta(weeks=delay)
    start = s + w #test start date delayed
    start_str = start.strftime("%Y-%m-%d")

    e = datetime.datetime.strptime(self.testEndDate,"%Y-%m-%d")
    w = datetime.timedelta(weeks=delay)
    end = e + w#end delayed
    end_str = end.strftime("%Y-%m-%d")
    #print('Test:', start_str, ':', end_str)
    test_data = df.loc[start_str:end_str]

    return wave_data, train_data, test_data


  def get_wave_dates_with_delay_yushu(self, delay):#yushu definition. 
    """
    Gets the wave data, train data, and test data after calculating delay.
    Wave start remains the same, wave end delayed. Train start remains the same, train end delayed. Test start and end delayed.
    Args:
      wave:Wave object
      delay (int): Delay in weeks
    Returns:
      wave_data (DataFrame): Wave data with delay
      train_data (DataFrame): Train data with delay
      test_data (DataFrame): Test data with delay
    """
    ############WAVE data
    start = datetime.datetime.strptime(self.startDate,"%Y-%m-%d")#start fixed, irrespective of delay
    start_str = start.strftime("%Y-%m-%d")

    e = datetime.datetime.strptime(self.endDate,"%Y-%m-%d")
    w = datetime.timedelta(weeks=delay)
    end = e + w#end delayed
    end_str = end.strftime("%Y-%m-%d")
    #print('Wave:', start_str, ':', end_str)
    wave_data = df.loc[start_str:end_str]

    ############Train data
    start = datetime.datetime.strptime(self.trainStartDate,"%Y-%m-%d")#train start fixed, irrespective of delay
    start_str = start.strftime("%Y-%m-%d")

    e = datetime.datetime.strptime(self.trainEndDate,"%Y-%m-%d")
    w = datetime.timedelta(weeks=delay)
    end = e + w#end delayed
    end_str = end.strftime("%Y-%m-%d")
    #print('Train:', start_str, ':', end_str)
    train_data = df.loc[start_str:end_str]

    ############Test data
    #trainEndDate here, that's how Yushu plotted the lines#but this will make incorrect predictions, for plot maybe do one week subtract if needed. so, testStartDate
    s = datetime.datetime.strptime(self.testStartDate,"%Y-%m-%d")#test start date delayed
    w = datetime.timedelta(weeks=delay)
    start = s + w #test start date delayed
    start_str = start.strftime("%Y-%m-%d")

    e = datetime.datetime.strptime(self.testEndDate,"%Y-%m-%d")
    w = datetime.timedelta(weeks=delay)
    end = e + w#end delayed
    end_str = end.strftime("%Y-%m-%d")
    #print('Test:', start_str, ':', end_str)
    test_data = df.loc[start_str:end_str]

    return wave_data, train_data, test_data

  def get_wave_test_start_date_with_delay(self, delay):#need to change this, yushu definition. 
    """
    Gets the test start date, enddate after calculating delay. Test start and end delayed.
    for plot display
    Args:
      wave:Wave object
      delay (int): Delay in weeks
    Returns:
      start_str (string): Test start date with delay
      end_str (string): Test end date with delay
    """
    s = datetime.datetime.strptime(self.testStartDate,"%Y-%m-%d")##test start date delayed
    w = datetime.timedelta(weeks=delay)
    start = s + w #test start date delayed
    start_str = start.strftime("%Y-%m-%d")

    e = datetime.datetime.strptime(self.testEndDate,"%Y-%m-%d")
    w = datetime.timedelta(weeks=delay)
    end = e + w#end delayed
    end_str = end.strftime("%Y-%m-%d")

    return start_str, end_str
    

  def get_wave_df(self):
    """
    Gets the wave data (from start date to end date) as a dataframe.
    Returns:
      self.df (DataFrame): Wave data as a dataframe
    """
    #return self.df[self.startDate:self.endDate]
    return self.df.loc[self.startDate:self.endDate]

  def get_wave_dates_with_delay(self, delay, Yushu):
    """
    Gets the wave data, train data, and test data after calculating delay.
    
    Args:
      wave:Wave object
      delay (int): Delay in weeks
      Yushu (boolean): True if Yushu's definition, False if JMM's definition
    Returns:
      wave_data (DataFrame): Wave data with delay
      train_data (DataFrame): Train data with delay
      test_data (DataFrame): Test data with delay
    """
    if Yushu == False:
      return self.get_wave_dates_with_delay_JMM(delay)
    
    return self.get_wave_dates_with_delay_yushu(delay)
