#include <fstream>
#include <string>

#include "TAxis.h"
#include "TCanvas.h"
#include "TDatime.h"
#include "TGraph.h"
#include "TROOT.h"
#include "TStyle.h"

TCanvas *graph_canvas;
TGraph *temperature_graph;
TGraph *pressure_graph;

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


void make_plot (std::vector<std::string> filenames)
{
  temperature_graph = new TGraph;
  pressure_graph = new TGraph;

  for (std::string filename : filenames)
    {
      std::ifstream data_file (filename);
      std::string data_line;

      // ";Title, http://www.gcdataconcepts.com, B1100-2, BMP085"
      getline(data_file, data_line);

      // ";Version, 995, Build date, Dec 26 2014,  SN:CCDC31101317663"
      getline(data_file, data_line);

      // ";Start_time, 2022-11-04, 11:04:30.000"
      getline(data_file, data_line);
      int start_year  = std::stoi(data_line.substr(13,4));
      int start_month = std::stoi(data_line.substr(18,2));
      int start_day   = std::stoi(data_line.substr(21,2));
      int start_hour  = std::stoi(data_line.substr(25,2));
      int start_min   = std::stoi(data_line.substr(28,2));
      int start_sec   = std::stoi(data_line.substr(31,2));

      TDatime start_date (start_year, start_month, start_day, start_hour, start_min, start_sec);
      const double start_time = start_date.Convert();

      // ";Temperature, XX.XX, deg C,  Vbat, XXXX, mv"
      getline(data_file, data_line);

      // ";SamplePeriod, XXXX,msec"
      getline(data_file, data_line);

      // ";Deadband, 0, counts"
      getline(data_file, data_line);

      // ";DeadbandTimeout, 0,sec"
      getline(data_file, data_line);

      // ";Time,Pressure(Pa),Temp(milliC)"
      getline(data_file, data_line);
  
      while (true)
	{
	  getline(data_file, data_line);

	  if (data_line[0] == ';') 
	    continue;
	  else if (data_line.empty())
	    break;

	  std::vector<double> values = split_string(data_line, ",");

	  if ((values.size() < 2) || (values.size() > 3)) {
	    printf("*** unexpected line : '%s'\n", data_line.c_str());
	    continue;}

	  // printf("%s\n", data_line.c_str());

	  double this_time = start_time + values[0];
	  pressure_graph->SetPoint(pressure_graph->GetN(), this_time, values[1]/100000);

	  if (values.size() == 3)
	    temperature_graph->SetPoint(temperature_graph->GetN(), this_time, values[2]/1000);
	}
    }

  graph_canvas = new TCanvas ("graph_canvas", "", 1400, 500);
  graph_canvas->Divide(2,1);

  graph_canvas->cd(1);
  temperature_graph->SetTitle(";;Temperature (C)");
  temperature_graph->GetXaxis()->SetTimeDisplay(1);
  temperature_graph->GetYaxis()->SetTitleOffset(1.25);
  temperature_graph->Draw("apl");

  graph_canvas->cd(2);
  pressure_graph->SetTitle(";;Pressure (bar)");
  pressure_graph->GetXaxis()->SetTimeDisplay(1);
  pressure_graph->GetYaxis()->SetTitleOffset(1.25);
  pressure_graph->Draw("apl");
}


void make_plot (const char *filename)
{
  std::vector<std::string> filenames;
  filenames.push_back(std::string(filename));
  make_plot (filename);
}

int main (int argc, char *argv[])
{
  gROOT->SetStyle("Plain");
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(1);
  gStyle->SetTitleBorderSize(0);

  std::vector<std::string> filenames;

  for (int iarg=1; iarg<argc; ++iarg)
    {
      std::string filename (argv[iarg]);
      filenames.push_back(filename);
    }

  make_plot(filenames);

  graph_canvas->SaveAs("graph_canvas.root");

  return 0;
}
