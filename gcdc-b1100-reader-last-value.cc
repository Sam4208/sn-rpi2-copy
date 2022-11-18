#include <fstream>
#include <string>
#include <stdio.h>
#include <time.h>
#include <vector>

std::vector<double> split_string (std::string str, std::string delimiter)
{
  size_t pos_start = 0, pos_end;
  const size_t delim_len = delimiter.length();

  std::string token;
  std::vector<double> split_str;

  while ((pos_end = str.find (delimiter, pos_start)) != std::string::npos)
    {
      token = str.substr(pos_start, pos_end - pos_start);
      pos_start = pos_end + delim_len;
      split_str.push_back(std::stod(token.c_str()));
  }

  split_str.push_back(atoi(str.substr(pos_start).c_str()));

  return split_str;
}


void read_file (const char *filename)
{
  int start_year  = 0;
  int start_month = 0;
  int start_day   = 0;
  int start_hour  = 0;
  int start_min   = 0;
  int start_sec   = 0;

  double last_time = 0;
  double last_pressure = 0;
  double last_temperature = 0;

  std::ifstream data_file (filename);

  if (!data_file.is_open())
    {
      printf("can not open '%s'\n", filename);
      return;
    }

  std::string data_line;

  // [HEADER_LINE1] ";Title, http://www.gcdataconcepts.com, B1100-2, BMP085"
  getline(data_file, data_line);

  // [HEADER_LINE2] ";Version, 995, Build date, Dec 26 2014,  SN:CCDC31101317663"
  getline(data_file, data_line);

  // [HEADER_LINE3] ";Start_time, 2022-11-04, 11:04:30.000"
  getline(data_file, data_line);
  start_year  = std::stoi(data_line.substr(13,4));
  start_month = std::stoi(data_line.substr(18,2));
  start_day   = std::stoi(data_line.substr(21,2));
  start_hour  = std::stoi(data_line.substr(25,2));
  start_min   = std::stoi(data_line.substr(28,2));
  start_sec   = std::stoi(data_line.substr(31,2));

  // [HEADER_LINE4] ";Temperature, XX.XX, deg C,  Vbat, XXXX, mv"
  getline(data_file, data_line);

  // [HEADER_LINE5] ";SamplePeriod, XXXX,msec"
  getline(data_file, data_line);

  // [HEADER_LINE6] ";Deadband, 0, counts"
  getline(data_file, data_line);

  // [HEADER_LINE7] ";DeadbandTimeout, 0,sec"
  getline(data_file, data_line);

  // [HEADER_LINE8] ";Time,Pressure(Pa),Temp(milliC)"
  getline(data_file, data_line);
  
  while (true)
    {
      // data line
      getline(data_file, data_line);

      if (data_line[0] == ';') 
	continue;
      else if (data_line.empty())
	break;

      std::vector<double> values = split_string(data_line, ",");

      if ((values.size() < 2) || (values.size() > 3))
	{
	  printf("*** unexpected line : '%s'\n", data_line.c_str());
	  continue;
	}

      last_time = values[0];

      last_pressure = values[1]/100000; // in bars

      if (values.size() == 3)
	last_temperature = values[2]/1000; // in degress
    }

  struct tm stop_time;
  stop_time.tm_year  = start_year - 1900;
  stop_time.tm_mon   = start_month - 1;
  stop_time.tm_mday  = start_day;
  stop_time.tm_hour  = start_hour;
  stop_time.tm_min   = start_min;
  stop_time.tm_sec   = start_sec + (int) (0.5 + last_time);
  mktime(&stop_time);
  
  char stop_time_buffer[24];
  strftime(stop_time_buffer, 24, "%Y-%m-%e %H:%M:%S", &stop_time);

  printf("%s\tP = %f\tT = %f\n", stop_time_buffer, last_pressure, last_temperature);

}


int main (int argc, char *argv[])
{
  if (argc < 2)
    {
      printf("usage: %s [FILE.CSV]\n", argv[0]);
      return 0;
    }

  read_file(argv[1]);

  return 0;
}
