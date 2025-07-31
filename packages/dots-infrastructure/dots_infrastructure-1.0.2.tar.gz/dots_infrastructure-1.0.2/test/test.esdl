<?xml version='1.0' encoding='UTF-8'?>
<esdl:EnergySystem xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:esdl="http://www.tno.nl/esdl" version="1" id="37e0284d-29f8-453e-91ec-2e7e02b5c16d" name="EnergySystem" description="Small energy system with assets used in GO-e" esdlVersion="v2211">
  <energySystemInformation xsi:type="esdl:EnergySystemInformation" id="8c79e632-1d89-4198-b055-157856e6fc9f">
    <carriers xsi:type="esdl:Carriers" id="02fafa20-a1bd-488e-a4db-f3c0ca7ff51a">
      <carrier xsi:type="esdl:ElectricityCommodity" id="d88696c0-b536-466b-adbf-429f282afeab" name="Electricity"/>
    </carriers>
  </energySystemInformation>
  <instance xsi:type="esdl:Instance" id="7972c9af-a7c9-4b06-9538-070cfa25291b" name="instance">
    <area xsi:type="esdl:Area" id="757e25b5-908f-4934-a16d-880c63c84406" name="area_title">
      <asset xsi:type="esdl:Bus" name="bus" id="44530afd-832b-4acf-998d-5654359ed813" voltage="400.0">
        <geometry xsi:type="esdl:Point" lat="51.444378637449404" lon="5.326824188232422"/>
        <port xsi:type="esdl:OutPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="a663919d-43e7-4cd5-8e04-01ed1fd8f7d5" id="072ad846-fa1f-43f5-a67d-a16df3f88d21"/>
      </asset>
      <asset xsi:type="esdl:Building" name="house1" id="00ab1742-0480-4a1d-a668-d09f5bca9e2f">
        <geometry xsi:type="esdl:Point" lat="51.44436826693578" lon="5.327478647232056"/>
        <asset xsi:type="esdl:EConnection" name="connection1" id="f006d594-0743-4de5-a589-a6c2350898da">
          <geometry xsi:type="esdl:Point" lat="260.0" lon="52.0" CRS="Simple"/>
          <port xsi:type="esdl:InPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="072ad846-fa1f-43f5-a67d-a16df3f88d21" id="a663919d-43e7-4cd5-8e04-01ed1fd8f7d5"/>
          <port xsi:type="esdl:InPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="296f937e-2e89-4be9-9d70-86f98a3de9ec" id="711a37c7-604c-4906-8e61-cec2b2c8e3bb"/>
          <port xsi:type="esdl:InPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="85b715d0-9851-40a4-a432-969245779b2f" id="33d0e20e-f618-4133-8eab-aa1bbb57e2ea"/>
        </asset>
        <asset xsi:type="esdl:PVInstallation" power="1000.0" name="pv-installation1" id="176af591-6d9d-4751-bb0f-fac7e99b1c3d" panelEfficiency="0.2">
          <geometry xsi:type="esdl:Point" lat="415.0" lon="236.0" CRS="Simple"/>
          <port xsi:type="esdl:OutPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="711a37c7-604c-4906-8e61-cec2b2c8e3bb" id="296f937e-2e89-4be9-9d70-86f98a3de9ec"/>
        </asset>
        <asset xsi:type="esdl:PVInstallation" power="1000.0" name="pv-installation1" id="b8766109-5328-416f-9991-e81a5cada8a6" panelEfficiency="0.2">
          <geometry xsi:type="esdl:Point" lat="365.0" lon="236.0" CRS="Simple"/>
          <port xsi:type="esdl:OutPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="33d0e20e-f618-4133-8eab-aa1bbb57e2ea" id="85b715d0-9851-40a4-a432-969245779b2f"/>
        </asset>
      </asset>
    </area>
  </instance>
  <services xsi:type="esdl:Services" id="7000c29e-8f08-4bd1-b420-5904767e297f">
    <service xsi:type="esdl:EnergyMarket" id="b612fc89-a752-4a30-84bb-81ebffc56b50" name="DA-market">
      <marketPrice xsi:type="esdl:DateTimeProfile">
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T00:15:00.000000" from="2020-01-14T00:00:00.000000" value="0.135"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T00:30:00.000000" from="2020-01-14T00:15:00.000000" value="0.135"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T00:45:00.000000" from="2020-01-14T00:30:00.000000" value="0.135"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T01:00:00.000000" from="2020-01-14T00:45:00.000000" value="0.135"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T01:15:00.000000" from="2020-01-14T01:00:00.000000" value="0.1172"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T01:30:00.000000" from="2020-01-14T01:15:00.000000" value="0.1172"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T01:45:00.000000" from="2020-01-14T01:30:00.000000" value="0.1172"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T02:00:00.000000" from="2020-01-14T01:45:00.000000" value="0.1172"/>
      </marketPrice>
    </service>
  </services>
</esdl:EnergySystem>
